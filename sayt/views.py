from django.shortcuts import render, redirect, get_object_or_404
from .models import market_databaze,MarketImage,saralangan,Izoh
from .forms import add_market,register
from django.contrib.auth import login,authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google import genai

client = genai.Client(api_key="AQ.Ab8RN6LzCJg21D0PQ1Z4ydgn2kzjum81gVevMdG4szVR6zk6Sw")

@csrf_exempt
def ai_chatbot(request):
    if request.method != "POST":
        return JsonResponse({"error": "Faqat POST so'rovlar qabul qilinadi"}, status=400)

    try:
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()

        if not user_message:
            return JsonResponse({"reply": "Iltimos, savolingizni yozing."})

        mahsulotlar = market_databaze.objects.all()
        baza_matni = "Bizning do'kondagi mavjud mahsulotlar ro'yxati:\n"
        for m in mahsulotlar:
            baza_matni += f"- Nomi: {getattr(m, 'title', str(m))}, Narxi: {getattr(m, 'narx', '')} so'm, Sifati: {getattr(m, 'sifati', '')}\n"

        prompt = f"""
        Siz 'olma market' elektron do'konining aqlli sun'iy intelekt yordamchisiz.
        Foydalanuvchiga faqat quyida berilgan mahsulotlar asosida o'zbek tilida qisqa va muloyim javob bering.
        Agar do'konda yo'q narsani so'rashsa, bizda hozircha yo'qligini ayting.
        Mahsulotlar bilan bog'liq bo'lmagan savollarga "Men faqat mahsulotlar haqida yordam bera olaman" deb javob bering.

        {baza_matni}
        Foydalanuvchi savoli: {user_message}
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return JsonResponse({"reply": response.text})

    except json.JSONDecodeError:
        return JsonResponse({"reply": "Xato: so'rov formati noto'g'ri."}, status=200)
    except Exception as e:
        print("Gemini xatosi:", repr(e))  # konsolda ko'rish uchun, foydalanuvchiga ko'rsatilmaydi
        return JsonResponse({"reply": "Kechirasiz, texnik xatolik yuz berdi. Birozdan so'ng qayta urinib ko'ring."}, status=200)
def logout_view(request):
    logout(request)  # Bu funksiya foydalanuvchi seansini o'chiradi (logaut qiladi)
    return redirect('login')  # Chiqib ketgandan keyin login sahifasiga yuboradi

def home_views(request):
    query = request.GET.get('search', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    
    # Sahifadan (URL'dan) sifat va tur qiymatlarini ushlab olamiz
    quality = request.GET.get('quality', '').strip()
    turi = request.GET.get('turi', '').strip()

    # Barcha mahsulotlarni olish
    marketlar = market_databaze.objects.all().order_by('-created_at') #

    # 1. Qidiruv so'rovi bo'yicha
    if query:
        marketlar = marketlar.filter(title__icontains=query) #

    # 2. Narxlar bo'yicha
    if min_price:
        marketlar = marketlar.filter(narx__gte=min_price) # Modelda 'narx' bo'lgani uchun o'zgartirildi
    if max_price:
        marketlar = marketlar.filter(narx__lte=max_price)

    # 3. Sifati bo'yicha filtr (yaxshi, o'rtacha, yomon)
    if quality:
        marketlar = marketlar.filter(sifati=quality)

    # 4. Mahsulot turi (Kategoriya) bo'yicha filtr (elektronika, musiqa, mebel)
    if turi:
        marketlar = marketlar.filter(maxsulot=turi)

    context = {
        'marketlar': marketlar,
        'query': query,
        'min_price': min_price,
        'max_price': max_price,
        'quality': quality,
        'turi': turi,
    }
    return render(request, "home.html", context) #

def profil_views(request):
    user_products = market_databaze.objects.filter(author=request.user)
    context = {
        'user_products': user_products
    }
    return render(request,"profil.html",context)

def detail_views(request, pk):
    # market_databaze modelidan ma'lumotni olamiz
    market = get_object_or_404(market_databaze, pk=pk)
    izohlar = market.izohlar.all().order_by('-vaqt')
    hamma_mahsulotlar = market_databaze.objects.exclude(pk=pk)[:8]

    if request.method == "POST":
        ism = request.POST.get('ism')
        matn = request.POST.get('matn')
        rating = request.POST.get('rating', 5)
        rasm = request.FILES.get('rasm') # Yuklangan rasmni olish

        # Izohni bazaga saqlash
        Izoh.objects.create(
            market=market,
            ism=ism,
            matn=matn,
            rating=int(rating),
            rasm=rasm
        )
        return redirect(request.path_info)
    context = {
        'market': market, 
        'izohlar': izohlar,
        'hamma_mahsulotlar': hamma_mahsulotlar
    }

    return render(request, 'index.html', context)


def add_malumot(request):
    if request.method == "POST":
        form = add_market(request.POST, request.FILES)
        if form.is_valid():
            mahsulot = form.save(commit=False)
            mahsulot.author = request.user 
            mahsulot.save()
            return redirect('home')
        images = request.FILES.getlist('images')
        for img in images:
            MarketImage.objects.create(market = mahsulot, images=img)
            return redirect('home')
    else:
        form = add_market()

    return render(request, 'add_yangilik.html', {'form': form})


def delet(request, id):  # 'i' argumenti 'id' ga almashtirildi
    market = get_object_or_404(market_databaze, id=id)
    market.delete()
    return redirect('profil')  # 'render' o'rniga to'g'ri 'redirect' qo'yildi

def register_view(request):
        if request.method == 'POST':
            form = register(request.POST,request.FILES)
            if form.is_valid():
                form.save()
                return redirect("login")
        else:
            form = register()
        return render(request,'register.html',{'form':form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid(): 
            # TO'G'RILANDI: 'passworld' emas, 'password' bo'lishi shart
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password') 
            
            # TO'G'RILANDI: password=password deb uzatiladi
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('home') # Endi ma'lumotni tekshirib, home.html ga o'tadi
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})
def edit_market(request, id):
    mahsulot = get_object_or_404(market_databaze, id=id)


    if request.method == "POST":
        form = add_market(request.POST, request.FILES, instance=mahsulot)
        if form.is_valid():
            form.save()
            images = request.FILES.getlist('images')
            for img in images:
                MarketImage.objects.create(market=mahsulot,images=img   )
            return redirect('profil')
    else:
        form = add_market(instance=mahsulot) 

    return render(request, 'edit_market.html', {'form': form,
     'existing_imges':mahsulot.gallery.all()})
@login_required
def toggle_saralangan(request, pk):
    if request.method == "POST":
        try:
            mahsulot = market_databaze.objects.get(pk=pk)
            # Agar oldin saralangan bo'lsa o'chiradi, bo'lmasa qo'shadi
            saralangan_item, created = saralangan.objects.get_or_create(user=request.user, mahsulot=mahsulot)
            
            if not created:
                saralangan_item.delete()
                status = "removed"
            else:
                status = "added"
                
            return JsonResponse({"status": status})
        except market_databaze.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Mahsulot topilmadi"}, status=404)
            
    return JsonResponse({"status": "error"}, status=400)

@login_required
def saralanganlar_sahifasi(request):
    # Foydalanuvchiga tegishli barcha saralangan ob'ektlarni olib, ichidagi mahsulotlarni HTML-ga chiqaramiz
    saralangan_obektlar = saralangan.objects.filter(user=request.user).select_related('mahsulot')
    
    # Biz bergan HTML faylida {% for market in saralangan_mahsulotlar %} deb yozilgan
    # Shuning uchun bu yerda list comprehension orqali faqat mahsulotlarning o'zini ajratib olamiz:
    mahsulotlar = [item.mahsulot for item in saralangan_obektlar]
    
    return render(request, 'saralanganlar.html', {
        'saralangan_mahsulotlar': mahsulotlar
    })
def savat_sahifasi(request):
    savat = request.session.get('savat', {})
    savat_mahsulotlari = []
    jami_narx = 0

    # Sessiyadagi har bir mahsulot ID si bo'yicha bazadan ma'lumotlarni olamiz
    for mahsulot_id, soni in savat.items():
        try:
            mahsulot = market_databaze.objects.get(pk=int(mahsulot_id))
            # Narxni raqamga o'girish (agar bazada satr bo'lsa, xato bermasligi uchun)
            narx_num = int(''.join(filter(str.isdigit, str(mahsulot.narx))))
            mahsulot_jami_narxi = narx_num * soni
            jami_narx += mahsulot_jami_narxi

            savat_mahsulotlari.append({
                'mahsulot': mahsulot,
                'soni': soni,
                'jami_narxi': mahsulot_jami_narxi
            })
        except market_databaze.DoesNotExist:
            continue

    context = {
        'savat_mahsulotlari': savat_mahsulotlari,
        'jami_narx': jami_narx
    }
    return render(request, 'savat.html', context)


def savatdan_ochirish(request, pk):
    savat = request.session.get('savat', {})
    mahsulot_id = str(pk)

    if mahsulot_id in savat:
        del savat[mahsulot_id] # Mahsulotni savatdan butunlay o'chirish
        request.session['savat'] = savat

    return redirect('savat_sahifasi')
def savatga_qoshish(request, pk):
    mahsulot = get_object_or_404(market_databaze, pk=pk)
    savat = request.session.get('savat', {})
    mahsulot_id = str(pk)
    
    if mahsulot_id in savat:
        savat[mahsulot_id] += 1
    else:
        savat[mahsulot_id] = 1
        
    request.session['savat'] = savat
    
    # MUHIM: Muvaffaqiyatli qo'shilganligi haqida xabar yuborish
    messages.success(request, f"Savatga 1 ta {mahsulot.title} qo'shildi!")
    
    return redirect(request.META.get('HTTP_REFERER', '/'))
        
    # 5. Yangilangan savat lug'atini qaytadan sessiyaga saqlaymiz
    request.session['savat'] = savat
    
    # 6. Foydalanuvchini kelgan sahifasiga (masalan, mahsulot tafsilotlari sahifasiga) qaytaramiz
    return redirect(request.META.get('HTTP_REFERER', '/'))