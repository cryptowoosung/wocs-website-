#!/usr/bin/env python3
"""
Build translations_cache.json from built-in dictionary.
No API needed. Covers all common UI, headings, labels, buttons.
Longer sentences stay in English (readable for international visitors).
"""
import json, os, re, glob

SITE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(SITE_DIR, 'data', 'translations_cache.json')

# ═══ COMPREHENSIVE 13-LANGUAGE DICTIONARY ═══
# Every entry: "EN": {"ja":"...", "zh":"...", ... all 13 langs}

def L(ja,zh,es,fr,de,pt="",it="",ar="",ru="",tr="",tw="",id_="",th=""):
    """Helper to build lang dict"""
    return {"ja":ja,"zh":zh,"es":es,"fr":fr,"de":de,
            "pt":pt or es,"it":it or es,"ar":ar,"ru":ru,
            "tr":tr,"tw":tw or zh,"id":id_,"th":th}

D = {
    # ══ UI / Buttons ══
    "Products": L("製品","产品","Productos","Produits","Produkte","Produtos","Prodotti","المنتجات","Продукция","Ürünler","產品","Produk","ผลิตภัณฑ์"),
    "Specifications": L("仕様","规格","Especificaciones","Spécifications","Spezifikationen","Especificações","Specifiche","المواصفات","Характеристики","Özellikler","規格","Spesifikasi","ข้อมูลจำเพาะ"),
    "Product Specifications": L("製品仕様","产品规格","Especificaciones","Spécifications Produit","Produktspezifikationen","Especificações","Specifiche Prodotto","مواصفات المنتج","Характеристики","Ürün Özellikleri","產品規格","Spesifikasi Produk","รายละเอียดผลิตภัณฑ์"),
    "Overview": L("概要","概述","Descripción","Aperçu","Überblick","Visão Geral","Panoramica","نظرة عامة","Обзор","Genel Bakış","概述","Ikhtisar","ภาพรวม"),
    "Download": L("ダウンロード","下载","Descargar","Télécharger","Herunterladen","Download","Scarica","تحميل","Скачать","İndir","下載","Unduh","ดาวน์โหลด"),
    "Explore": L("探索","探索","Explorar","Explorer","Entdecken","Explorar","Esplora","استكشف","Обзор","Keşfet","探索","Jelajahi","สำรวจ"),
    "View More": L("もっと見る","查看更多","Ver Más","Voir Plus","Mehr Sehen","Ver Mais","Vedi Altro","عرض المزيد","Подробнее","Daha Fazla","查看更多","Lihat Lebih","ดูเพิ่มเติม"),
    "Contact Us": L("お問い合わせ","联系我们","Contáctenos","Contactez-nous","Kontaktieren","Fale Conosco","Contattaci","اتصل بنا","Связаться","Bize Ulaşın","聯繫我們","Hubungi Kami","ติดต่อเรา"),
    "Request Quote": L("見積もり依頼","获取报价","Solicitar Cotización","Demander un Devis","Angebot Anfordern","Solicitar Orçamento","Richiedi Preventivo","طلب عرض سعر","Запросить Цену","Teklif İste","索取報價","Minta Penawaran","ขอใบเสนอราคา"),
    "Quote Inquiry": L("見積もり相談","报价咨询","Consulta","Demande de Devis","Angebotsanfrage","Consulta","Richiesta","استفسار","Запрос Цены","Teklif Sorgusu","報價諮詢","Permintaan Harga","สอบถามราคา"),
    "Free Consultation": L("無料相談","免费咨询","Consulta Gratuita","Consultation Gratuite","Kostenlose Beratung","Consulta Gratuita","Consulenza Gratuita","استشارة مجانية","Бесплатная Консультация","Ücretsiz Danışma","免費諮詢","Konsultasi Gratis","ปรึกษาฟรี"),
    "Free Consultation →": L("無料相談 →","免费咨询 →","Consulta Gratuita →","Consultation Gratuite →","Kostenlose Beratung →","Consulta Gratuita →","Consulenza Gratuita →","استشارة مجانية →","Бесплатная Консультация →","Ücretsiz Danışma →","免費諮詢 →","Konsultasi Gratis →","ปรึกษาฟรี →"),
    "Details →": L("詳細 →","详情 →","Detalles →","Détails →","Details →","Detalhes →","Dettagli →","تفاصيل →","Подробнее →","Detaylar →","詳情 →","Detail →","รายละเอียด →"),
    "Learn More →": L("詳しく見る →","了解更多 →","Ver Más →","En Savoir Plus →","Mehr Erfahren →","Saiba Mais →","Scopri di Più →","اعرف المزيد →","Узнать Больше →","Daha Fazla →","了解更多 →","Selengkapnya →","เรียนรู้เพิ่มเติม →"),
    "Learn More in Detail": L("もっと詳しく","详细了解","Más Detalles","Plus de Détails","Mehr Details","Mais Detalhes","Più Dettagli","تفاصيل أكثر","Подробнее","Daha Detaylı","詳細了解","Lebih Detail","เรียนรู้เพิ่มเติม"),
    "View All": L("すべて見る","查看全部","Ver Todo","Voir Tout","Alle Ansehen","Ver Tudo","Vedi Tutto","عرض الكل","Показать Все","Tümünü Gör","查看全部","Lihat Semua","ดูทั้งหมด"),
    "Free": L("無料","免费","Gratis","Gratuit","Kostenlos","Grátis","Gratis","مجاني","Бесплатно","Ücretsiz","免費","Gratis","ฟรี"),
    "Subscribe": L("購読","订阅","Suscribirse","S'abonner","Abonnieren","Assinar","Iscriviti","اشترك","Подписаться","Abone Ol","訂閱","Berlangganan","สมัครรับข่าว"),
    "Home": L("ホーム","首页","Inicio","Accueil","Startseite","Início","Home","الرئيسية","Главная","Ana Sayfa","首頁","Beranda","หน้าแรก"),
    "Blog": L("ブログ","博客","Blog","Blog","Blog","Blog","Blog","مدونة","Блог","Blog","部落格","Blog","บล็อก"),
    "Inquiry": L("お問い合わせ","咨询","Consulta","Demande","Anfrage","Consulta","Richiesta","استفسار","Запрос","Sorgu","諮詢","Permintaan","สอบถาม"),
    "?": L("？","？","?"," ?","?","?","?","؟","?","?","？","?","?"),
    
    # ══ Form fields ══
    "Name *": L("お名前 *","姓名 *","Nombre *","Nom *","Name *","Nome *","Nome *","الاسم *","Имя *","İsim *","姓名 *","Nama *","ชื่อ *"),
    "Email *": L("メール *","邮箱 *","Email *","Email *","E-Mail *","Email *","Email *","البريد *","Email *","E-posta *","電郵 *","Email *","อีเมล *"),
    "Country *": L("国 *","国家 *","País *","Pays *","Land *","País *","Paese *","البلد *","Страна *","Ülke *","國家 *","Negara *","ประเทศ *"),
    "Phone": L("電話","电话","Teléfono","Téléphone","Telefon","Telefone","Telefono","هاتف","Телефон","Telefon","電話","Telepon","โทรศัพท์"),
    "Message": L("メッセージ","留言","Mensaje","Message","Nachricht","Mensagem","Messaggio","رسالة","Сообщение","Mesaj","留言","Pesan","ข้อความ"),
    "Contact Person *": L("担当者 *","联系人 *","Contacto *","Personne *","Ansprechpartner *","Contato *","Referente *","جهة الاتصال *","Контактное лицо *","İlgili Kişi *","聯繫人 *","Kontak *","ผู้ติดต่อ *"),
    "Desired Quantity": L("希望数量","期望数量","Cantidad","Quantité","Menge","Quantidade","Quantità","الكمية","Количество","Miktar","數量","Jumlah","จำนวน"),
    "Installation Site": L("設置場所","安装地点","Ubicación","Lieu","Standort","Local","Luogo","الموقع","Место","Konum","安裝地點","Lokasi","สถานที่"),
    "Budget Range": L("予算","预算范围","Presupuesto","Budget","Budget","Orçamento","Budget","الميزانية","Бюджет","Bütçe","預算","Anggaran","งบประมาณ"),
    "Additional Notes": L("追加メモ","补充说明","Notas","Notes","Anmerkungen","Notas","Note","ملاحظات","Примечания","Notlar","補充說明","Catatan","หมายเหตุ"),
    
    # ══ Stats / Badges ══
    "16 Years": L("16年","16年","16 Años","16 Ans","16 Jahre","16 Anos","16 Anni","16 سنة","16 Лет","16 Yıl","16年","16 Tahun","16 ปี"),
    "Experience": L("経験","经验","Experiencia","Expérience","Erfahrung","Experiência","Esperienza","خبرة","Опыт","Deneyim","經驗","Pengalaman","ประสบการณ์"),
    "Patent": L("特許","专利","Patente","Brevet","Patent","Patente","Brevetto","براءة","Патент","Patent","專利","Paten","สิทธิบัตร"),
    "Filed": L("出願済み","已申请","Presentada","Déposé","Eingereicht","Registrada","Depositato","مودعة","Подана","Başvuruldu","已申請","Diajukan","ยื่นแล้ว"),
    "Warranty": L("保証","保修","Garantía","Garantie","Garantie","Garantia","Garanzia","ضمان","Гарантия","Garanti","保固","Garansi","การรับประกัน"),
    "Completed": L("完了","已完成","Completado","Terminé","Abgeschlossen","Concluído","Completato","مكتمل","Завершено","Tamamlandı","已完成","Selesai","เสร็จสิ้น"),
    "Zero Middleman Markup": L("中間マージンゼロ","零中间加价","Sin Intermediarios","Zéro Intermédiaire","Null Zwischenhandel","Sem Intermediários","Zero Intermediari","بدون وسطاء","Без Посредников","Sıfır Aracı","零中間加價","Tanpa Perantara","ไม่มีคนกลาง"),
    "Export to 120+ Countries": L("120カ国以上に輸出","出口120+国家","120+ Países","120+ Pays","120+ Länder","120+ Países","120+ Paesi","120+ دولة","120+ Стран","120+ Ülke","出口120+國家","120+ Negara","120+ ประเทศ"),
    "On-site Installation": L("現場施工","现场安装","Instalación In Situ","Installation sur Site","Vor-Ort-Montage","Instalação no Local","Installazione in Loco","تركيب في الموقع","Монтаж на Месте","Yerinde Kurulum","現場安裝","Instalasi di Lokasi","ติดตั้งหน้างาน"),
    "Own Factory": L("自社工場","自有工厂","Fábrica Propia","Usine Propre","Eigene Fabrik","Fábrica Própria","Fabbrica Propria","مصنع خاص","Свой Завод","Kendi Fabrikası","自有工廠","Pabrik Sendiri","โรงงานของเรา"),
    "Proven Quality": L("品質保証","品质保证","Calidad Probada","Qualité Prouvée","Bewährte Qualität","Qualidade Comprovada","Qualità Provata","جودة مثبتة","Проверенное Качество","Kanıtlanmış Kalite","品質保證","Kualitas Terbukti","คุณภาพพิสูจน์แล้ว"),
    "Proven Global Quality": L("実証済みグローバル品質","全球品质保证","Calidad Global","Qualité Mondiale","Globale Qualität","Qualidade Global","Qualità Globale","جودة عالمية","Глобальное Качество","Küresel Kalite","全球品質保證","Kualitas Global","คุณภาพระดับโลก"),
    "Global Certified": L("グローバル認証","全球认证","Certificación Global","Certifié Mondial","Global Zertifiziert","Certificado Global","Certificato Globale","معتمد عالمياً","Глобальный Сертификат","Küresel Sertifika","全球認證","Bersertifikat Global","ได้รับการรับรองระดับโลก"),
    "Technical Support": L("技術サポート","技术支持","Soporte Técnico","Support Technique","Technischer Support","Suporte Técnico","Supporto Tecnico","دعم فني","Техподдержка","Teknik Destek","技術支持","Dukungan Teknis","ฝ่ายเทคนิค"),
    "Parts Replacement": L("部品交換","部件更换","Reemplazo","Remplacement","Ersatzteile","Substituição","Ricambi","قطع غيار","Замена Деталей","Parça Değişimi","部件更換","Penggantian","เปลี่ยนชิ้นส่วน"),
    
    # ══ Product categories ══
    "D-Series Domes": L("D-シリーズ ドーム","D系列穹顶","Domos Serie D","Dômes Série D","D-Serie Kuppeln","Domos Série D","Cupole Serie D","قباب السلسلة D","Купола Серии D","D Serisi Kubbeler","D系列穹頂","Kubah Seri D","โดมซีรีส์ D"),
    "S-Series": L("S-シリーズ","S系列","Serie S","Série S","S-Serie","Série S","Serie S","السلسلة S","Серия S","S Serisi","S系列","Seri S","ซีรีส์ S"),
    "Signature Series": L("Signatureシリーズ","Signature系列","Serie Signature","Série Signature","Signature Serie","Série Signature","Serie Signature","سلسلة Signature","Серия Signature","Signature Serisi","Signature系列","Seri Signature","ซีรีส์ Signature"),
    "Modular Systems": L("モジュラーシステム","模块系统","Sistemas Modulares","Systèmes Modulaires","Modulare Systeme","Sistemas Modulares","Sistemi Modulari","أنظمة معيارية","Модульные Системы","Modüler Sistemler","模組系統","Sistem Modular","ระบบโมดูลาร์"),
    "Weldless Joint": L("無溶接ジョイント","无焊接接头","Junta sin Soldadura","Joint sans Soudure","Schweißfreies Gelenk","Junta sem Solda","Giunto senza Saldatura","وصلة بدون لحام","Безсварное Соединение","Kaynaksız Bağlantı","無焊接接頭","Sambungan Tanpa Las","ข้อต่อไร้เชื่อม"),
    "Available": L("利用可能","可选","Disponible","Disponible","Verfügbar","Disponível","Disponibile","متاح","Доступно","Mevcut","可選","Tersedia","มีจำหน่าย"),
    "Various": L("各種","各种","Varios","Divers","Verschiedene","Vários","Vari","متنوع","Различные","Çeşitli","各種","Beragam","หลากหลาย"),
    "Configuration": L("構成","配置","Configuración","Configuration","Konfiguration","Configuração","Configurazione","تكوين","Конфигурация","Yapılandırma","配置","Konfigurasi","การกำหนดค่า"),
    "Furniture": L("家具","家具","Mobiliario","Mobilier","Möbel","Mobiliário","Arredi","أثاث","Мебель","Mobilya","家具","Furnitur","เฟอร์นิเจอร์"),
    "Frame": L("フレーム","框架","Marco","Cadre","Rahmen","Estrutura","Telaio","إطار","Рама","Çerçeve","框架","Rangka","เฟรม"),
    "Cover": L("カバー","覆盖","Cubierta","Couverture","Abdeckung","Cobertura","Copertura","غطاء","Покрытие","Örtü","覆蓋","Penutup","ผ้าคลุม"),
    "Type": L("タイプ","类型","Tipo","Type","Typ","Tipo","Tipo","نوع","Тип","Tip","類型","Tipe","ประเภท"),
    "Capacity": L("収容人数","容量","Capacidad","Capacité","Kapazität","Capacidade","Capacità","سعة","Вместимость","Kapasite","容量","Kapasitas","ความจุ"),
    "Customer": L("お客様","客户","Cliente","Client","Kunde","Cliente","Cliente","عميل","Клиент","Müşteri","客戶","Pelanggan","ลูกค้า"),
    "Reviews": L("レビュー","评价","Reseñas","Avis","Bewertungen","Avaliações","Recensioni","تقييمات","Отзывы","Yorumlar","評價","Ulasan","รีวิว"),
    "Cases": L("事例","案例","Casos","Études de Cas","Fallstudien","Casos","Casi","حالات","Кейсы","Vakalar","案例","Kasus","กรณีศึกษา"),
    "Construction": L("施工","施工","Construcción","Construction","Bau","Construção","Costruzione","بناء","Строительство","İnşaat","施工","Konstruksi","การก่อสร้าง"),
    "Showroom": L("ショールーム","展厅","Sala de Exposición","Showroom","Showroom","Showroom","Showroom","صالة العرض","Шоурум","Showroom","展廳","Showroom","โชว์รูม"),
    "Applications": L("活用分野","应用领域","Aplicaciones","Applications","Anwendungen","Aplicações","Applicazioni","التطبيقات","Применение","Uygulamalar","應用領域","Aplikasi","การใช้งาน"),
    "Project": L("プロジェクト","项目","Proyecto","Projet","Projekt","Projeto","Progetto","مشروع","Проект","Proje","項目","Proyek","โครงการ"),
    
    # ══ Why WOCS / CTA ══
    "Why WOCS": L("なぜWOCS","为什么选WOCS","¿Por qué WOCS","Pourquoi WOCS","Warum WOCS","Por que WOCS","Perché WOCS","لماذا WOCS","Почему WOCS","Neden WOCS","為什麼WOCS","Mengapa WOCS","ทำไม WOCS"),
    "Elevate Your Space Value with": L("空間の価値を高める","提升空间价值","Eleve su Espacio con","Valorisez Votre Espace","Werten Sie Ihren Raum auf","Eleve seu Espaço","Valorizza il Tuo Spazio","ارفع قيمة مساحتك","Повысьте Ценность","Alanınızı Yükseltin","提升空間價值","Tingkatkan Nilai Ruang","เพิ่มคุณค่าพื้นที่"),
    "Signature Series Solutions": L("Signatureシリーズ","Signature系列方案","Soluciones Signature","Solutions Signature","Signature Lösungen","Soluções Signature","Soluzioni Signature","حلول Signature","Решения Signature","Signature Çözümleri","Signature系列方案","Solusi Signature","โซลูชัน Signature"),
    "Stay Updated": L("最新情報","获取最新消息","Manténgase Informado","Restez Informé","Bleiben Sie Informiert","Fique Atualizado","Resta Aggiornato","ابق على اطلاع","Будьте в Курсе","Güncel Kalın","獲取最新消息","Tetap Update","อัปเดตข่าวสาร"),
    "Get Materials": L("資料請求","获取资料","Obtener Materiales","Obtenir Documents","Material Erhalten","Obter Materiais","Ottieni Materiali","احصل على المواد","Получить Материалы","Materyal Al","獲取資料","Dapatkan Materi","รับเอกสาร"),
    "Explore Projects": L("プロジェクトを見る","浏览项目","Explorar Proyectos","Explorer les Projets","Projekte Entdecken","Explorar Projetos","Esplora Progetti","استكشف المشاريع","Обзор Проектов","Projeleri Keşfet","瀏覽項目","Jelajahi Proyek","สำรวจโครงการ"),
    "Discover Spaces Created by WOCS": L("WOCSが作った空間","探索WOCS打造的空间","Descubra Espacios WOCS","Découvrez les Espaces WOCS","WOCS Räume Entdecken","Descubra Espaços WOCS","Scopri gli Spazi WOCS","اكتشف مساحات WOCS","Откройте Пространства WOCS","WOCS Alanlarını Keşfedin","探索WOCS打造的空間","Temukan Ruang WOCS","พบพื้นที่จาก WOCS"),
    "You May Also Like": L("こちらもおすすめ","您可能还喜欢","También le Puede Gustar","Vous Aimerez Aussi","Das Könnte Ihnen Gefallen","Você Também Pode Gostar","Potrebbe Piacerti","قد يعجبك أيضاً","Вам Может Понравиться","İlginizi Çekebilir","您可能還喜歡","Mungkin Anda Suka","คุณอาจชอบ"),
    "Other Applications": L("その他の活用","其他应用","Otras Aplicaciones","Autres Applications","Weitere Anwendungen","Outras Aplicações","Altre Applicazioni","تطبيقات أخرى","Другие Применения","Diğer Uygulamalar","其他應用","Aplikasi Lainnya","การใช้งานอื่น"),
    "From Our Blog": L("ブログより","来自博客","De Nuestro Blog","De Notre Blog","Aus Unserem Blog","Do Nosso Blog","Dal Nostro Blog","من مدونتنا","Из Блога","Blogumuzdan","來自部落格","Dari Blog Kami","จากบล็อกของเรา"),
    "Learn More": L("詳しく見る","了解更多","Ver Más","En Savoir Plus","Mehr Erfahren","Saiba Mais","Scopri di Più","اعرف المزيد","Узнать Больше","Daha Fazla","了解更多","Selengkapnya","เรียนรู้เพิ่มเติม"),
    "Product Lineup": L("製品ラインナップ","产品阵容","Línea de Productos","Gamme de Produits","Produktpalette","Linha de Produtos","Gamma Prodotti","تشكيلة المنتجات","Линейка Продукции","Ürün Yelpazesi","產品陣容","Jajaran Produk","กลุ่มผลิตภัณฑ์"),
    
    # ══ Showroom ══
    "At Hwasun Showroom": L("華順ショールームで","在华顺展厅","En el Showroom Hwasun","Au Showroom Hwasun","Im Hwasun Showroom","No Showroom Hwasun","Allo Showroom Hwasun","في صالة عرض هواسون","В Шоуруме Хвасун","Hwasun Showroom'da","在華順展廳","Di Showroom Hwasun","ที่โชว์รูมฮวาซุน"),
    "See for Yourself": L("直接ご確認ください","亲自确认","Compruébelo","Vérifiez par Vous-même","Überzeugen Sie Sich","Veja por Si Mesmo","Verifichi di Persona","تحقق بنفسك","Убедитесь Лично","Kendiniz Görün","親自確認","Lihat Sendiri","มาดูด้วยตาตนเอง"),
    "Extra 5% Discount on Visit": L("ご来場で5%追加割引","到访额外5%折扣","5% Descuento Adicional","5% Réduction Supplémentaire","5% Extra-Rabatt","5% Desconto Adicional","5% Sconto Extra","خصم 5% إضافي","Доп. Скидка 5%","Ziyarette %5 Ek İndirim","到訪額外5%折扣","Diskon 5% Tambahan","ส่วนลดเพิ่ม 5%"),
    "Book Showroom Visit": L("ショールーム予約","预约展厅参观","Reservar Visita","Réserver une Visite","Showroom-Besuch Buchen","Agendar Visita","Prenota Visita","حجز زيارة","Забронировать Визит","Ziyaret Planla","預約展廳","Booking Kunjungan","จองเยี่ยมชม"),
    
    # ══ Blog / Content ══
    "Complete Glamping Startup Guide": L("グランピング創業完全ガイド","完整露营创业指南","Guía Completa de Glamping","Guide Complet Glamping","Glamping Startup Guide","Guia Completo Glamping","Guida Completa Glamping","دليل بدء التخييم","Полное Руководство","Glamping Başlangıç Kılavuzu","完整露營創業指南","Panduan Lengkap Glamping","คู่มือแกลมปิ้ง"),
    "Glamping ROI Analysis": L("グランピング投資収益分析","露营投资回报分析","Análisis ROI Glamping","Analyse ROI Glamping","Glamping ROI Analyse","Análise ROI Glamping","Analisi ROI Glamping","تحليل عائد الاستثمار","Анализ ROI Глэмпинг","Glamping ROI Analizi","露營投資回報分析","Analisis ROI Glamping","วิเคราะห์ ROI แกลมปิ้ง"),
    "Permitting Process A to Z": L("許認可プロセス A to Z","许可流程A到Z","Proceso de Permisos A-Z","Processus de Permis A-Z","Genehmigungsverfahren A-Z","Processo de Licenças A-Z","Processo Autorizzazioni A-Z","عملية التراخيص A-Z","Процесс Разрешений A-Z","İzin Süreci A-Z","許可流程A到Z","Proses Perizinan A-Z","กระบวนการอนุญาต A-Z"),
    
    # ══ Short labels ══
    "Certified": L("認証","认证","Certificado","Certifié","Zertifiziert","Certificado","Certificato","معتمد","Сертифицировано","Sertifikalı","認證","Bersertifikat","ได้รับการรับรอง"),
    "Related": L("関連","相关","Relacionado","Associé","Verwandt","Relacionado","Correlato","ذات صلة","Связанное","İlgili","相關","Terkait","เกี่ยวข้อง"),
    "Popular": L("人気","热门","Popular","Populaire","Beliebt","Popular","Popolare","شائع","Популярное","Popüler","熱門","Populer","ยอดนิยม"),
    "Core": L("コア","核心","Núcleo","Essentiel","Kern","Núcleo","Nucleo","جوهر","Ключевой","Çekirdek","核心","Inti","หลัก"),
    "Specs": L("スペック","规格","Especificaciones","Spécifications","Spezifikationen","Especificações","Specifiche","المواصفات","Характеристики","Özellikler","規格","Spesifikasi","สเปค"),
    "Cost &": L("コスト &","费用 &","Costo &","Coût &","Kosten &","Custo &","Costo &","التكلفة &","Стоимость &","Maliyet &","費用 &","Biaya &","ต้นทุน &"),
    "Technology &": L("技術 &","技术 &","Tecnología &","Technologie &","Technologie &","Tecnologia &","Tecnologia &","التقنية &","Технология &","Teknoloji &","技術 &","Teknologi &","เทคโนโลยี &"),
    "Estimated": L("予想","预估","Estimado","Estimé","Geschätzt","Estimado","Stimato","متوقع","Ожидаемый","Tahmini","預估","Estimasi","ประมาณการ"),
    "Average": L("平均","平均","Promedio","Moyenne","Durchschnitt","Média","Media","متوسط","Средний","Ortalama","平均","Rata-rata","เฉลี่ย"),
    "Optimistic": L("楽観的","乐观","Optimista","Optimiste","Optimistisch","Otimista","Ottimistico","متفائل","Оптимистичный","İyimser","樂觀","Optimis","มองในแง่ดี"),
    "Annual Revenue": L("年間売上","年收入","Ingresos Anuales","Revenus Annuels","Jahresumsatz","Receita Anual","Ricavi Annuali","الإيرادات السنوية","Годовой Доход","Yıllık Gelir","年收入","Pendapatan Tahunan","รายได้ต่อปี"),
    "Annual Net Profit": L("年間純利益","年净利润","Beneficio Neto Anual","Bénéfice Net Annuel","Jahresnettogewinn","Lucro Líquido Anual","Utile Netto Annuale","صافي الربح السنوي","Годовая Чистая Прибыль","Yıllık Net Kâr","年淨利潤","Laba Bersih Tahunan","กำไรสุทธิต่อปี"),
    "Annual ROI": L("年間ROI","年ROI","ROI Anual","ROI Annuel","Jährlicher ROI","ROI Anual","ROI Annuale","العائد السنوي","Годовой ROI","Yıllık ROI","年ROI","ROI Tahunan","ROI ต่อปี"),
}

# ═══ BUILD CACHE ═══
cache = {}
for en, langs in D.items():
    cache[en] = langs

# Also match all EN strings from pages
with open('/tmp/all_en.json','r') as f:
    all_en = json.load(f)

matched = sum(1 for s in all_en if s in cache)
print(f"Dictionary covers {matched}/{len(all_en)} unique strings ({matched/len(all_en)*100:.1f}%)")
print(f"Remaining {len(all_en)-matched} strings will show in English (fallback)")

# Save cache
os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
with open(CACHE_FILE, 'w', encoding='utf-8') as f:
    json.dump(cache, f, ensure_ascii=False, indent=2)

print(f"✅ Saved {len(cache)} translations to {CACHE_FILE}")

# ═══ APPLY TO HTML ═══
LANGS = ['ja','zh','es','fr','de','pt','it','ar','ru','tr','tw','id','th']

html_files = glob.glob(os.path.join(SITE_DIR, '**', '*.html'), recursive=True)
html_files = [f for f in html_files if f != os.path.join(SITE_DIR, 'index.html')]

updated = 0
total_keys = 0
for filepath in html_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'WOCS_PAGE_TR' not in content:
        continue
    
    tr_start = content.find('WOCS_PAGE_TR={')
    tr_end = content.find(';\n', tr_start) + 2
    tr_block = content[tr_start:tr_end]
    
    ko_m = re.search(r'ko:\{([^}]*)\}', tr_block)
    en_m = re.search(r'en:\{([^}]*)\}', tr_block)
    if not ko_m or not en_m:
        continue
    
    ko_items = dict(re.findall(r'(\w+):"([^"]*)"', ko_m.group(1)))
    en_items = dict(re.findall(r'(\w+):"([^"]*)"', en_m.group(1)))
    
    lang_items = {lang: {} for lang in LANGS}
    for key, en_val in en_items.items():
        if en_val in cache:
            for lang in LANGS:
                if lang in cache[en_val]:
                    tr = cache[en_val][lang]
                    if tr and tr != en_val:
                        lang_items[lang][key] = tr
                        total_keys += 1
    
    all_langs = ['ko','en'] + LANGS
    parts = []
    for lang in all_langs:
        if lang == 'ko':
            s = ','.join(f'{k}:"{v}"' for k,v in ko_items.items())
        elif lang == 'en':
            s = ','.join(f'{k}:"{v}"' for k,v in en_items.items())
        else:
            items = lang_items.get(lang, {})
            s = ','.join(f'{k}:"{v}"' for k,v in items.items()) if items else ''
        parts.append(f'{lang}:{{{s}}}')
    
    new_tr = 'WOCS_PAGE_TR={' + ',\n'.join(parts) + '\n};\n'
    content = content[:tr_start] + new_tr + content[tr_end:]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    updated += 1

print(f"✅ Updated {updated} pages with {total_keys} language-specific keys")
print(f"\n나중에 Gemini API 할당량이 복구되면 translate_all.py를 실행하여")
print(f"나머지 {len(all_en)-matched}개 문장도 13개 언어로 번역 가능합니다.")
