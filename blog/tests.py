from io import BytesIO
from tempfile import TemporaryDirectory

from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Post


class PostImageUploadTests(TestCase):
    def setUp(self):
        media = TemporaryDirectory()
        self.addCleanup(media.cleanup)
        storage_settings = override_settings(
            MEDIA_ROOT=media.name,
            MEDIA_URL='/test-media/',
            STORAGES={
                'default': {
                    'BACKEND': 'django.core.files.storage.FileSystemStorage',
                    'OPTIONS': {'location': media.name, 'base_url': '/test-media/'},
                },
                'staticfiles': {
                    'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
                },
            },
        )
        storage_settings.enable()
        self.addCleanup(storage_settings.disable)
        self.user = get_user_model().objects.create_user(username='author')
        self.client.force_login(self.user)
        self.data = {
            'title': 'Pictures', 'slug': 'pictures', 'body': 'A post',
            'john': 'John', 'health': 'Good', 'health_rating': '4.0',
            'status': Post.Status.PUBLISHED,
        }

    def picture(self, color='red'):
        content = BytesIO()
        Image.new('RGB', (2, 2), color).save(content, format='PNG')
        return SimpleUploadedFile('picture.png', content.getvalue(), 'image/png')

    def create_post(self):
        response = self.client.post(
            reverse('blog:post_create'), {**self.data, 'image': self.picture()},
        )
        post = Post.objects.latest('pk')
        self.assertRedirects(response, post.get_absolute_url())
        return post

    def test_upload_uses_model_directory_and_configured_storage_url(self):
        post = self.create_post()
        self.assertTrue(post.image.name.startswith('blog_images/'))
        self.assertTrue(post.image.storage.exists(post.image.name))
        self.assertEqual(post.image.url, '/test-media/' + post.image.name)
        response = self.client.get(post.get_absolute_url())
        self.assertContains(response, post.image.url)

    def test_edit_without_upload_retains_image(self):
        post = self.create_post()
        original = post.image.name
        response = self.client.post(reverse('blog:post_edit', args=[post.pk]), self.data)
        self.assertRedirects(response, post.get_absolute_url())
        post.refresh_from_db()
        self.assertEqual(post.image.name, original)

    def test_replacement_with_same_filename_preserves_original_file(self):
        post = self.create_post()
        original = post.image.name
        with post.image.open('rb') as uploaded:
            original_bytes = uploaded.read()
        response = self.client.post(
            reverse('blog:post_edit', args=[post.pk]),
            {**self.data, 'image': self.picture('blue')},
        )
        self.assertRedirects(response, post.get_absolute_url())
        post.refresh_from_db()
        self.assertNotEqual(post.image.name, original)
        with post.image.storage.open(original, 'rb') as uploaded:
            self.assertEqual(uploaded.read(), original_bytes)

    def test_editor_can_clear_existing_image(self):
        post = self.create_post()
        edit_url = reverse('blog:post_edit', args=[post.pk])
        self.assertContains(self.client.get(edit_url), 'name="image-clear"')
        response = self.client.post(edit_url, {**self.data, 'image-clear': 'on'})
        self.assertRedirects(response, post.get_absolute_url())
        post.refresh_from_db()
        self.assertFalse(post.image)

    def test_invalid_image_is_rejected(self):
        response = self.client.post(reverse('blog:post_create'), {
            **self.data,
            'image': SimpleUploadedFile('fake.png', b'not an image', 'image/png'),
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('image', response.context['form'].errors)
        self.assertFalse(Post.objects.exists())
