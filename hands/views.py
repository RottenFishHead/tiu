from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Hands
from poker.models import PokerSession
from .forms import HandsForm
from .card_images import CARD_IMAGES
from .tasks import send_email_task, send_mail_func
import json
from django.forms.models import model_to_dict
from django.template.loader import render_to_string
from django.db.models import Count, Exists, OuterRef


@login_required
def add_hand(request, session_id):
    session = get_object_or_404(PokerSession, id=session_id)
    form = HandsForm(initial={
        "hero": request.user,
        "session": session_id 
    })

    if request.method == 'POST':
        form = HandsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("poker:session_hands")

    return render(request, 'hands/hand_form.html', {'form': form, 'session': session})

@login_required
def edit_hand(request, hand_id):
    hand = get_object_or_404(Hands, id=hand_id)
    if request.method == 'POST':
        form = HandsForm(request.POST, instance=hand)
        if form.is_valid():
            form.save()
            return redirect(hand)
    else:
        form = HandsForm(instance=hand)
    return render(request, 'hands/hand_form.html', {'form':form})

@login_required
def delete_hand(request, hand_id):
    hand = get_object_or_404(Hands, id=hand_id)
    if request.method == 'POST':
        hand.delete()
        return redirect('hands:hands_list')  # Replace 'hands_list' with the URL pattern name for the hands list view
    return render(request, 'hands/hand_confirm_delete.html', {'hand': hand})

@login_required
def hand_detail(request, hand_id):
    hand = get_object_or_404(Hands, id=hand_id)
    hand_dict = model_to_dict(hand)
    hero_card_1_image_url = CARD_IMAGES.get(hand.hero_card_1)
    hero_card_2_image_url = CARD_IMAGES.get(hand.hero_card_2)
    villian_card_1_image_url = CARD_IMAGES.get(hand.villian_card_1)
    villian_card_2_image_url = CARD_IMAGES.get(hand.villian_card_2)
    flop1_image_url = CARD_IMAGES.get(hand.flop1)
    flop2_image_url = CARD_IMAGES.get(hand.flop2)
    flop3_image_url = CARD_IMAGES.get(hand.flop3)
    turn_image_url = CARD_IMAGES.get(hand.turn)
    river_image_url = CARD_IMAGES.get(hand.river)
    
    # #For Email
    # hand_dict['hero_card_1'] = hand.hero_card_1
    # hand_dict['hero_card_2'] = hand.hero_card_2
    # hand_dict['villian_card_1'] = hand.villian_card_1
    # hand_dict['villian_card_2'] = hand.villian_card_2
    # hand_dict['player1_card_1'] = hand.player1_card_1
    # hand_dict['player1_card_2'] = hand.player1_card_2
    # hand_dict['player2_card_1'] = hand.player2_card_1
    # hand_dict['player2_card_2'] = hand.player2_card_2
    # hand_dict['flop1'] = hand.flop1
    # hand_dict['flop2'] = hand.flop2
    # hand_dict['flop3'] = hand.flop3
    # hand_dict['turn'] = hand.turn
    # hand_dict['hero_position'] = hand.hero_position
    # hand_dict['villian_position'] = hand.villian_position
    # hand_dict['villian_image'] = hand.villian_image
    # hand_dict['hero_image'] = hand.hero_image
    # hand_dict['villian_stack'] = hand.villian_stack
    # hand_dict['hero_stack'] = hand.hero_stack
    # hand_dict['flop_action'] = hand.flop_action
    # hand_dict['turn_action'] = hand.turn_action
    # hand_dict['river_action'] = hand.river_action
    # hand_dict['notes'] = hand.notes
    
    # serialized_details = json.dumps(hand_dict)
    # email_body = render_to_string('hands/email/hand_template.html', hand_dict)
    # send_email_task.delay(serialized_details, email_body)

    context = {
        'hero_card_1_image_url': hero_card_1_image_url,
        'hero_card_2_image_url': hero_card_2_image_url,
        'villian_card_1_image_url': villian_card_1_image_url,
        'villian_card_2_image_url': villian_card_2_image_url,
        'flop1_image_url': flop1_image_url,
        'flop2_image_url': flop2_image_url,
        'flop3_image_url': flop3_image_url,
        'turn_image_url': turn_image_url,
        'river_image_url': river_image_url,
        'hand': hand
       
   }
    
    return render(request, 'hands/hand_detail.html', context)

@login_required
def sessison_hands_list(request, session_id):
    session = get_object_or_404(PokerSession, id=session_id)
    hands = Hands.objects.filter(session_id=session_id)

    context = {
        'hands': hands, 
        'session': session
    }
    return render(request, 'hands/session_hands_list.html', context)



def send_mail_to_all(request): 
    send_mail_func.delay()  
    return HttpResponse("Sent Email Successfully...Check your mail please")