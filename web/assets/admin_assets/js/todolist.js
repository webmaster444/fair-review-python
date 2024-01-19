(function($) {
  'use strict';
  $(function() {
    var todoListItem = $('.todo-list');
    var todoListInput = $('.todo-list-input');
    $('.todo-list-add-btn').on("click", function(event) {
      event.preventDefault();

      var storeUrl = $(this).prevAll('.todo-list-input').val();
      var storeValue = $(this).prevAll('#productStore').val();
      var storeName = $('#productStore').find('option[value="'+storeValue+'"]').html();
      
      if (storeUrl && storeName) {
        todoListItem.append('<li><div class="form-check" storeID="'+storeValue+'">' + storeName + ' - ' + storeUrl + '</div><i class="remove mdi mdi-close-circle-outline"></i></li>');
        todoListInput.val("");
        let storeInfoVal = $("#storeInfo").val();
        let jsonStoreInfo;
        if(storeInfoVal == "" || storeInfoVal == undefined || storeInfoVal == null){
          jsonStoreInfo = [];
        }else{          
          jsonStoreInfo = JSON.parse(storeInfoVal);
        }
        
        jsonStoreInfo.push({
          "Store ID": storeValue,
          "Store Name": storeName,
          "Store URL": storeUrl,
          "psID": ""
        })

        $("#storeInfo").val(JSON.stringify(jsonStoreInfo));
      }

    });

    todoListItem.on('change', '.checkbox', function() {
      if ($(this).attr('checked')) {
        $(this).removeAttr('checked');
      } else {
        $(this).attr('checked', 'checked');
      }

      $(this).closest("li").toggleClass('completed');

    });

    todoListItem.on('click', '.remove', function() {
      $(this).parent().remove();
      let storeId = $(this).parent().find('.form-check').attr('storeid');
      let storeInfoVal = $("#storeInfo").val();
      let jsonStoreInfo = JSON.parse(storeInfoVal);
      jsonStoreInfo.forEach((d, i, obj)=>{
        if(d['Store ID'] == storeId){
          obj.splice(i, 1);
        }
      });
      $('#storeInfo').val(JSON.stringify(jsonStoreInfo));
    });

  });
})(jQuery);