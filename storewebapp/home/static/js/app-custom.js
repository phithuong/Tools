$(".owl-carousel").on("initialized.owl.carousel", () => {
    setTimeout(() => {
      $(".owl-item.active .owl-slide-animated").addClass("is-transitioned");
      $("section").show();
    }, 200);
  });
  
  const $owlCarousel = $(".owl-carousel").owlCarousel({
    items: 1,
    loop: true,
    autoplay:true,
    autoplayTimeout:10000,
    autoplayHoverPause:true
  });
  
  $owlCarousel.on("changed.owl.carousel", e => {
    $(".owl-slide-animated").removeClass("is-transitioned");
  
    const $currentOwlItem = $(".owl-item").eq(e.item.index);
    $currentOwlItem.find(".owl-slide-animated").addClass("is-transitioned");
  
    const $target = $currentOwlItem.find(".owl-slide-text");
    doDotsCalculations($target);
  });
  
  $owlCarousel.on("resize.owl.carousel", () => {
    setTimeout(() => {
      setOwlDotsPosition();
    }, 50);
  });
  
  /*if there isn't content underneath the carousel*/
  //$owlCarousel.trigger("refresh.owl.carousel");
  
  setOwlDotsPosition();
  
  function setOwlDotsPosition() {
    const $target = $(".owl-item.active .owl-slide-text");
    doDotsCalculations($target);
  }
  
  function doDotsCalculations(el) {
    const height = el.height();
    const {top, left} = el.position();
    const res = height + top + 20;
  
    $(".owl-carousel .owl-dots").css({
      top: `${res}px`,
      left: `${left}px`
    });
  }