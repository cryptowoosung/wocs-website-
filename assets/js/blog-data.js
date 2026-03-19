/* ============================================================
   WOCS 블로그 데이터
   새 글: 배열 맨 위에 객체 추가 → 자동 반영
   category uses translation keys — render with t(p.category)
   title/excerpt use translation keys — render with t(p.title) / t(p.excerpt)
   ============================================================ */
var BLOG_POSTS = [
{
  id:10, title:"bt10", excerpt:"be10",
  date:"2026-03-05", category:"cat_construction", featured:true,
  image:"https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800&h=500&fit=crop&q=85",
  content:'bc10'
},
{
  id:9, title:"bt9", excerpt:"be9",
  date:"2026-03-02", category:"cat_case", featured:true,
  image:"https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&h=500&fit=crop&q=85",
  content:'bc9'
},
{
  id:8, title:"bt8", excerpt:"be8",
  date:"2026-02-26", category:"cat_revenue", featured:true,
  image:"https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&h=500&fit=crop&q=85",
  content:'bc8'
},
{
  id:7, title:"bt7", excerpt:"be7",
  date:"2026-02-20", category:"cat_startup", featured:false,
  image:"https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&h=500&fit=crop&q=85",
  content:'bc7'
},
{
  id:6, title:"bt6", excerpt:"be6",
  date:"2026-02-14", category:"cat_permit", featured:true,
  image:"https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=800&h=500&fit=crop&q=85",
  content:'bc6'
},
{
  id:5, title:"bt5", excerpt:"be5",
  date:"2026-02-08", category:"cat_startup", featured:true,
  image:"https://images.unsplash.com/photo-1510798831971-661eb04b3739?w=800&h=500&fit=crop&q=85",
  content:'bc5'
},
{
  id:4, title:"bt4", excerpt:"be4",
  date:"2026-02-01", category:"cat_construction", featured:true,
  image:"https://images.unsplash.com/photo-1513828583688-c52646db42da?w=800&h=500&fit=crop&q=85",
  content:'bc4'
},
{
  id:3, title:"bt3", excerpt:"be3",
  date:"2026-01-25", category:"cat_construction", featured:false,
  image:"https://images.unsplash.com/photo-1517299321609-52687d1bc55a?w=800&h=500&fit=crop&q=85",
  content:'bc3'
},
{
  id:2, title:"bt2", excerpt:"be2",
  date:"2026-01-15", category:"cat_revenue", featured:false,
  image:"https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800&h=500&fit=crop&q=85",
  content:'bc2'
},
{
  id:1, title:"bt1", excerpt:"be1",
  date:"2026-01-05", category:"cat_startup", featured:false,
  image:"https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800&h=500&fit=crop&q=85",
  content:'bc1'
}
];

var BLOG_CATEGORIES = ["cat_all","cat_startup","cat_construction","cat_trend","cat_revenue","cat_permit","cat_case"];
