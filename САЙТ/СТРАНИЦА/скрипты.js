// Наш скрипт. В копии этим занимаются бандлы Next.js, здесь нужно ровно одно:
// раскрытие вопросов. Класс и анимация — родные, из стилей копии.
document.addEventListener('click', function (e) {
  var вопрос = e.target.closest('.FAQItem_question__KohP_');
  if (!вопрос) return;
  var пункт = вопрос.closest('.FAQItem_faqItem___Jz2R');
  пункт.classList.toggle('FAQItem_faqItemOpened__8wvcD');
});

// С клавиатуры: вопрос помечен role="button", значит должен открываться
// пробелом и вводом, иначе блок недоступен без мыши.
document.addEventListener('keydown', function (e) {
  if (e.key !== 'Enter' && e.key !== ' ') return;
  var вопрос = e.target.closest && e.target.closest('.FAQItem_question__KohP_');
  if (!вопрос) return;
  e.preventDefault();
  вопрос.closest('.FAQItem_faqItem___Jz2R').classList.toggle('FAQItem_faqItemOpened__8wvcD');
});
