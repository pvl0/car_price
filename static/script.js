$(document).ready(function() {
    $('.manufacturer').select2({
        placeholder: 'Manufacturer',
        })
    $('.model').select2({
        placeholder: 'Model',
        })
    $('.year').select2({
        placeholder: 'Year',
        })

        // chaining manufacturer and model
        let manufacturer_select = document.getElementById('manufacturer');
        let model_select = document.getElementById('model');
        
        manufacturer_select.onchange = function() {
            manufacturer = manufacturer_select.value;
            // fetch models (comes from app.route in app.py flask file) спижжено з якогось відоса на ютб
            fetch('/models/' + manufacturer).then(function(response) {
                response.json().then(function(data) {
                    let optionHTML = '';

                    for (let model of data.models) {
                        optionHTML += '<option value="' + model.id + '">' + model.name + '</option>';
                    }
                   
                    model_select.innerHTML = optionHTML; // заповнюємо опції форми з моделлю авто

                });
            });
        };
        // end of chaining
        
        // $('.submitForm').on('click', function(){
        //     $().delay(2000);
        //     $('#manufacturer').val(manufacturer_select.value).trigger('change');
        //     $('#model').val(model_select.value).trigger('change');
        // });
    });
    