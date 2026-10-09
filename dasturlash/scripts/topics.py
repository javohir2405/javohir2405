# 25 ta mavzu (Namunaviy dastur 48-72-mavzulari, tartib saqlangan). (nom, shakl, mustaqil_soat)
N, A = 'Nazariy', 'Amaliy'
TOPICS = [
 ("GUI muhitida grafik imkoniyatlar. GUI muhitida grafik holat, tasvirlarni va funksiya grafiklarini qurish (Chart).", N, 1),
 ("Muloqot oynalari bilan ishlash. GUI muhitida muloqot oynalari va ularni sozlash, boshqarish elementlari.", A, 1),
 ("Muloqot oynalari bilan ishlash. GUI muhitida muloqot oynalarini bir-biri bilan bog‘lash va xabar oynalarini shakllantirish.", A, 0),
 ("GUI muhitida foydalanuvchi interfeysi. Kichik loyihalar bilan ishlash.", N, 1),
 ("Shablon (template) tushunchasi va ularning qo‘llanilishi. Muloqot oynalari bilan ishlash.", A, 1),
 ("Konteyner sinflar. Chiziqli konteynerlar (array, vector).", N, 1),
 ("Konteyner sinflar. Konteynerlar (kolleksiyalar). Chiziqli konteynerlar (list, forward_list, deque).", A, 0),
 ("Assosiativ va tartiblanmagan assosiativ konteynerlar. Assosiativ konteynerlar (set, multiset).", N, 1),
 ("Assosiativ va tartiblanmagan assosiativ konteynerlar. Assosiativ konteynerlar (map, multimap).", A, 1),
 ("Konteyner adapterlari. Stack, queue, priority_queue.", N, 1),
 ("Sonli sinflar va ular bilan ishlash (valarray, slice, gslice).", A, 0),
 ("Visual Studio muhitida dasturlash. GUI muhitida menyular va uskunalar paneli.", N, 1),
 ("Visual Studio muhitida dasturlash. GUI muhitida menyular va uskunalar paneli bilan amaliy ishlash.", A, 0),
 ("Formalarning xossa va xususiyati.", N, 1),
 ("Formalarni bir-biriga bog‘lash.", A, 1),
 ("Komponentalar bilan ishlash. Ularning xossa va xususiyatlari asosida ishlov berish.", A, 0),
 ("Ma’lumotlarni kiritish va chiqarish komponentalari.", N, 1),
 ("Matnlar bilan ishlovchi komponentalar va ularning xossa hamda xususiyatlari.", A, 1),
 ("Tarmoqlanish va tanlash uchun mo‘ljallangan komponentalar.", A, 0),
 ("Massivlar bilan ishlash komponentalari.", N, 1),
 ("Muloqot oynalari va ularni sozlash, boshqarish elementlari. MessageBox ni shakllantirish. Muloqot oynalarini shakllantirishga oid vazifalar.", A, 1),
 ("To‘g‘ri chiziq va turli xil geometrik figuralarni chizish.", A, 0),
 ("VS ning grafik imkoniyatlari. Tasvirlash bilan ishlash komponentalari.", N, 1),
 ("Chart komponentasi yordamida funksiya grafiklarini qurish.", A, 1),
 ("GUI muhitida foydalanuvchi interfeysi. Kichik loyihalar bilan ishlash.", A, 0),
]
assert len(TOPICS)==25
assert sum(1 for t in TOPICS if t[1]==N)==10 and sum(1 for t in TOPICS if t[1]==A)==15
assert sum(t[2] for t in TOPICS)==17
