$(document).ready(function(){
  var scrollTop = 0;
  $(window).scroll(function(){
    scrollTop = $(window).scrollTop();
     $('.counter').html(scrollTop);
    
    if (scrollTop >= 200) {
      $('#nav-home').addClass('scrolled-nav');
    } else if (scrollTop < 500) {
      $('#nav-home').removeClass('scrolled-nav');
    } 
    
  }); 
  
});