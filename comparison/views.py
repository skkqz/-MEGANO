from django.db.models import Prefetch
from django.shortcuts import render, redirect
from product.models import Product, ProductProperty
from django.views import View
from product.services import get_category


class Comparison(View):

    def get(self, request):
        com = request.session.get('comparison')
        goods_item = list()
        if com is None:
            return redirect('/')
        for item in com:
            goods_items = Product.objects.filter(id=item['id']).prefetch_related(Prefetch(
                'property',
                queryset=ProductProperty.objects.select_related(
                    'product',
                    'property',
                    )))
            goods_item.append(goods_items)
        categories = get_category()
        content = {'goods_item': goods_item, 'categories': categories}
        return render(request, 'comparison/comparison.html', content)


class ComparisonAdd(View):
    def post(self, request, id):
        if not request.session.get('comparison'):
            request.session['comparison'] = list()
        else:
            request.session['comparison'] = list(request.session['comparison'])
        item_exist = next(
                (item for item in request.session['comparison'] if item['type'] == request.POST.get('type')
                 and item['id'] == id), False)
        add_data = {
                'type': request.POST.get('type'),
                'id': id
            }
        if not item_exist:
            request.session['comparison'].append(add_data)
            request.session.modified = True
        return redirect('comparison:comparison')


class ComparisonRemove(View):
    def post(self, request, id):
        for item in request.session['comparison']:
            if item['id'] == id and item['type'] == request.POST.get('type'):
                item.clear()
                while {} in request.session['comparison']:
                    request.session['comparison'].remove({})
                if not request.session['comparison']:
                    del request.session['comparison']
        request.session.modified = True
        return redirect('comparison:comparison')


class ComparisonDelete(View):
    def post(self, request):
        if request.session.get('comparison'):
            del request.session['comparison']
        return redirect('/')
