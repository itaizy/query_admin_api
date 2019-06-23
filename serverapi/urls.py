from django.conf.urls import url
from . import views#导入views
app_name = 'serverapi'

urlpatterns = [
    #aaa$代表以aaa结束，views.index是关联对应views.py中的一个函数
    url(r'^aaa$', views.index, name='index'),
    url(r'^qqscorefree$', views.qqscorefree, name='qqscorefree'),
    url(r'^logincode$', views.logincode, name='logincode'),
    url(r'^regiuserinfo$', views.regiuserinfo, name='regiuserinfo'),
    url(r'^getPostUsers$', views.getPostUsers, name='getPostUsers'),
    url(r'^getscorelist$', views.getscorelist, name='getscorelist'),
    url(r'^payme$', views.payme, name='payme'),
    url(r'^payed$', views.payed, name='payed'),
    url(r'^descpay$', views.descpay, name='descpay'),
    url(r'^tableheader$', views.tableheader, name='tableheader'),
]
#本步骤目前做这个可以写，可以不写，不过之后要是对student做具体操作（比如：增删改等）必须写，方便管理项目。
#如果不打算写，可以直接做完第1步，直接第2步
