$(".datetime").each(function(v,c){c.textContent=moment(c.textContent).format('DD MMMM YYYY, h:mm a')});

$(".btn").click(function(btn){
    console.log(this);
});

function copyToClipboard(element) {
  var $temp = $("<input>");
  $("body").append($temp);
  $temp.val($(element).text()).select();
  document.execCommand("copy");
  $temp.remove();
}
