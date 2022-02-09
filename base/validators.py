from django.core.paginator import EmptyPage
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

SpecialSym =['$', '@', '#', '%', '!', '&', '^', '-', '_', '=', '+' ]

def paginate(data, paginator, pagenumber):
    if int(pagenumber) > paginator.num_pages:
        raise ValidationError(_("Not enough pages"), code=404)
    try:
        previous_page_number = paginator.page(pagenumber).previous_page_number()
    except EmptyPage:
        previous_page_number = None
    try:
        next_page_number = paginator.page(pagenumber).next_page_number()
    except EmptyPage:
        next_page_number = None
    data_to_show = paginator.page(pagenumber).object_list
    return {
        'pagination': {
            'previous_page': previous_page_number,
            'is_previous_page': paginator.page(pagenumber).has_previous(),
            'next_page': next_page_number,
            'is_next_page': paginator.page(pagenumber).has_next(),
            'start_index': paginator.page(pagenumber).start_index(),
            'end_index': paginator.page(pagenumber).end_index(),
            'total_entries': paginator.count,
            'total_pages': paginator.num_pages,
            'page': int(pagenumber)
        },
        'results': data_to_show
    }

def validate_pw(pw):
    res = True
    if len(pw) < 8:
        res = False
        raise ValidationError(_("Password length should be at least 8 characters"), code=404)
    if not any(char.isdigit() for char in pw):
        res = False
        raise ValidationError("Password should contain atleast one number", code=404)
    if not any(char.isupper() for char in pw):
        res = False
        raise ValidationError("Password should contain at least one uppercase character", code=404)
    if not any(char.islower() for char in pw):
        print('Password should have at least one lowercase letter')
        res = False
        raise ValidationError("Password should contain at least one lowercase character", code=404)
    if not any(char in SpecialSym for char in pw):
        res = False
        raise ValidationError("Password should contain at least one special character", code=404)
    if res:
        return res

def validate_name(pw):
    res = True
    if any(char.isdigit() for char in pw):
        res = False
        raise ValidationError("Name should not contain numbers", code=404)
    if any(char in SpecialSym for char in pw):
        res = False
        raise ValidationError("Name should not contain special characters", code=404)
    if res:
        return res

def validate_phone_no(value):
    try:
        pass
    except Exception as e:
        print(e)