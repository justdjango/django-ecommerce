from django import template
from django.utils.safestring import mark_safe

from core.models import Slide

register = template.Library()


@register.simple_tag
def slides():
    items = Slide.objects.filter(is_active=True).order_by('pk')
    items_div = ""
    for i in items:
        items_div += """<div class="item-slick1 item2-slick1" style="background-image: url(/media/{});"><div class="wrap-content-slide1 sizefull flex-col-c-m p-l-15 p-r-15 p-t-150 p-b-170"><span class="caption1-slide1 m-text1 t-center animated visible-false m-b-15" data-appear="rollIn">{}</span><h2 class="caption2-slide1 xl-text1 t-center animated visible-false m-b-37" data-appear="lightSpeedIn">{}</h2><div class="wrap-btn-slide1 w-size1 animated visible-false" data-appear="slideInUp"><a href="{}" class="flex-c-m size2 bo-rad-23 s-text2 bgwhite hov1 trans-0-4">Shop Now</a></div></div></div>""".format(i.image, i.caption1, i.caption2, i.link)
    return mark_safe(items_div)


