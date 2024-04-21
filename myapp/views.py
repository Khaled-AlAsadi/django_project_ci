from django.http import Http404,HttpResponseRedirect
from django.shortcuts import redirect, render

from myapp.forms import RoadSignForm, TraficRuleForm
from .models import TraficRule, TraficRuleAnswer, TraficRuleChoice, TraficRuleQuestion, RoadSign
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator

# Create your views here.


def index(request):
    if not isinstance(request.user, AnonymousUser):
        questions = TraficRuleQuestion.objects.all()
        total_traficRules_questions = TraficRuleQuestion.objects.count()
        answered_questions = TraficRuleAnswer.objects.filter(
            user=request.user, is_answered=True).count()

        if total_traficRules_questions > 0:
            progress_percentage = (
                answered_questions / total_traficRules_questions) * 100
        else:
            progress_percentage = 0

        return render(request, 'home.html', {"questions": questions, "progress_percentage": int(progress_percentage)})
    else:
        return HttpResponseRedirect('login')


def trafic_rules(request):
    if not isinstance(request.user, AnonymousUser):
        rules = TraficRule.objects.all()
        paginated = Paginator(rules, 1)
        page_number = request.GET.get('page')

        page = paginated.get_page(page_number)
        return render(request, 'trafic_rules.html', {'page': page})
    else:
        return HttpResponseRedirect('login')

def start_quiz(request):
    first_question = TraficRuleQuestion.objects.first()
    return redirect('trafic_rule_question_detail', question_id=first_question.id)


def continue_quiz(request):
    # Get all answered question IDs
    # Flat retrives a single field
    answered_question_ids = TraficRuleAnswer.objects.values_list(
        'question_id', flat=True)

    # Get the first question that hasn't been answered
    first_unanswered_question = TraficRuleQuestion.objects.exclude(
        id__in=answered_question_ids).first()

    return redirect('trafic_rule_question_detail', question_id=first_unanswered_question.id)


def next_question(request, current_question_id):
    try:
        # id__gt = greater than
        next_question = TraficRuleQuestion.objects.filter(
            id__gt=current_question_id).order_by('id').first()
        if next_question:
            return redirect('trafic_rule_question_detail', question_id=next_question.id)
    except TraficRuleQuestion.DoesNotExist:
        return redirect('question_not_found')


def previous_question(request, current_question_id):
    try:
        # id__lt = less than
        previous_question = TraficRuleQuestion.objects.filter(
            id__lt=current_question_id).order_by('id').first()
        if previous_question:
            return redirect('trafic_rule_question_detail', question_id=previous_question.id)
        else:
            raise Http404("Previous question does not exist")
    except TraficRuleQuestion.DoesNotExist:
        raise Http404("Previous question does not exist")


def trafic_rule_question_detail(request, question_id):
    if not isinstance(request.user, AnonymousUser):
        question = get_object_or_404(TraficRuleQuestion, pk=question_id)
        choices = question.traficrulechoice_set.all()
        last_question_id = TraficRuleQuestion.objects.last().id
        first_question_id = TraficRuleQuestion.objects.first().id
        is_last_question = question_id == last_question_id
        is_first_question = question_id == first_question_id
        message = ''
        is_answered_correctly = False

        if request.method == "POST":
            submitted_answer_id = request.POST.get('choice')
            if submitted_answer_id:
                submitted_choice = TraficRuleChoice.objects.get(
                    pk=submitted_answer_id)
                if submitted_choice.is_correct:
                    message = "Your answer is correct!"
                    is_answered_correctly = True
                    existing_answer = TraficRuleAnswer.objects.filter(
                        question=question, user=request.user).first()
                    if existing_answer:
                        existing_answer.is_answered = True
                        existing_answer.save()
                    else:
                        answer = TraficRuleAnswer.objects.create(
                            question=question, user=request.user, is_answered=True)
                        answer.selected_choices.add(submitted_choice)
                    existing_answer = TraficRuleAnswer.objects.filter(
                        question=question, user=request.user).first()
                    for choice in choices:
                        if choice in existing_answer.selected_choices.all():
                            choice.is_selected = True
                else:
                    message = "Sorry, your answer is wrong."
            else:
                message = "Please select an answer."

        elif request.method == "GET":
            existing_answer = TraficRuleAnswer.objects.filter(
                question=question, user=request.user).first()
            if existing_answer:
                for choice in choices:
                    if choice in existing_answer.selected_choices.all():
                        choice.is_selected = True
                        is_answered_correctly = True
        return render(request, 'question_detail.html', {'question': question, 'choices': choices, 'message': message, 'is_answered_correctly': is_answered_correctly, 'current_question_id': question_id, "last_question_id": last_question_id, "is_last_question": is_last_question, "is_first_question": is_first_question})
    else:
        return HttpResponseRedirect('login')


def road_signs_page(request):
    if not isinstance(request.user, AnonymousUser):
        road_signs = RoadSign.objects.all()
        paginated = Paginator(road_signs, 1)
        page_number = request.GET.get('page')
        page = paginated.get_page(page_number)
        return render(request, 'road_signs_page.html', {'page': page})
    else:
        return HttpResponseRedirect('login')

# create view for RoadSign
def create_roadSign_view(request):
    # dictionary for initial data with 
    # field names as keys
    context ={}
 
    # add the dictionary during initialization
    form = RoadSignForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('road_signs')

    context['form']= form
    return render(request, "create_roadSign_view.html", context)

# delete view for RoadSign
def delete_roadSign_view(request, id):
    # dictionary for initial data with 
    # field names as keys
    context ={}
 
    # fetch the object related to passed id
    obj = get_object_or_404(RoadSign, id = id)
 
 
    if request.method =="POST":
        # delete object
        obj.delete()
        # after deleting redirect to 
        # home page
        return redirect('road_signs')
 
    return render(request, "delete_roadsign_view.html", context)

# update view for RoadSign
def update_roadSign_view(request, id):
    context = {}

    # Fetch the object related to the passed id
    obj = get_object_or_404(RoadSign, id=id)

    # Pass the object as an instance in the form
    form = RoadSignForm(request.POST or None, instance=obj)
    # Save the data from the form and redirect to detail_view
    if form.is_valid():
        form.save()
        return redirect('road_signs')

    # Add form dictionary to context
    context["form"] = form

    return render(request, "update_roadsign_view.html", context)


# create view for TraficRule
def create_traficrule_view(request):
    # dictionary for initial data with 
    # field names as keys
    context ={}
 
    # add the dictionary during initialization
    form = TraficRuleForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('trafic_rules')

    context['form']= form
    return render(request, "create_traficrule_view.html", context)


# delete view for TraficRule
def delete_traficrule_view(request, id):
    context = {}

    # Fetch the TraficRule object related to the passed id
    obj = get_object_or_404(TraficRule, id=id)

    if request.method == "POST":
        # Delete the object
        obj.delete()
        # After deleting, redirect to the home page
        return redirect('trafic_rules')

    return render(request, "delete_traficrule_view.html", context)

# update view for RoadSign
def update_traficRule_view(request, id):
    context = {}

    # Fetch the object related to the passed id
    obj = get_object_or_404(TraficRule, id=id)

    # Pass the object as an instance in the form
    form = TraficRuleForm(request.POST or None, instance=obj)
    # Save the data from the form and redirect to detail_view
    if form.is_valid():
        form.save()
        return redirect('trafic_rules')

    # Add form dictionary to context
    context["form"] = form

    return render(request, "update_roadsign_view.html", context)