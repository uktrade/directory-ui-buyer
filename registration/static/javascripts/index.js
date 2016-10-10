(function(){

  var marketing_source_element = document.getElementById('id_marketing_source');

  var marketing_source_bank_wrapper = document.getElementById('marketing_source_bank');
  var marketing_source_bank_input = document.getElementById('id_marketing_source_bank');

  var marketing_source_other_wrapper = document.getElementById('marketing_source_other');
  var marketing_source_other_input = document.getElementById('id_marketing_source_other');

  var FORM_CONTROL_HIDDEN = 'form-group hidden';
  var FORM_CONTROL_VISIBLE = 'form-group';
  var OTHER = 'other';
  var BANK = 'Bank';


  function updateMarketingSourceFields() {
    // Get the select value;
    var value = marketing_source_element.value;

    if (value === BANK) {
      marketing_source_bank_wrapper.className = FORM_CONTROL_VISIBLE;
      marketing_source_other_wrapper.className = FORM_CONTROL_HIDDEN;
      marketing_source_other_input.value = '';
    } else if (value === OTHER) {
      marketing_source_bank_wrapper.className = FORM_CONTROL_HIDDEN;
      marketing_source_bank_input.value = '';
      marketing_source_other_wrapper.className = FORM_CONTROL_VISIBLE;
    } else {
      marketing_source_bank_wrapper.className = FORM_CONTROL_HIDDEN;
      marketing_source_bank_input.value = '';
      marketing_source_other_wrapper.className = FORM_CONTROL_HIDDEN;
      marketing_source_other_input.value = '';
    }
  }


  if (marketing_source_element.addEventListener) {
    marketing_source_element.addEventListener('change', updateMarketingSourceFields);
  } else {
    marketing_source_element.attachEvent('onchange', updateMarketingSourceFields);
  }

  updateMarketingSourceFields();

})();
