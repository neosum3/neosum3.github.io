//For auto adjust input box size: (not used now)

$.fn.textWidth = function(text, font) {

    if (!$.fn.textWidth.fakeEl) $.fn.textWidth.fakeEl = $('<span>').hide().appendTo(document.body);

    $.fn.textWidth.fakeEl.text(text || this.val() || this.text() || this.value() || this.attr('placeholder')).css('font', font || this.css('font'));

    return $.fn.textWidth.fakeEl.width();
};

$('.width-dynamic').on('input', function() {
    var inputWidth = $(this).textWidth() + 10;
    $(this).css({
        width: inputWidth
    })
}).trigger('input');


function inputWidth(elem, minW, maxW) {
    elem = $(this) ;
    console.log(elem)
}

var targetElem = $('.width-dynamic');

inputWidth(targetElem);