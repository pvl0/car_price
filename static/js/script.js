$(document).ready(function() {
    $('.manufacturer').select2({
        placeholder: 'Marka',
        theme: 'classic',
        }).one('select2:open', function(e) {
            $('input.select2-search__field').prop('placeholder', 'Marka ...');
        });
    $('.model').select2({
        placeholder: 'Model',
        theme: 'classic',
        }).one('select2:open', function(e) {
            $('input.select2-search__field').prop('placeholder', 'Model ...');
        });
    $('.year').select2({
        placeholder: 'Rocznik',
        theme: 'classic',
        }).one('select2:open', function(e) {
            $('input.select2-search__field').prop('placeholder', 'Rocznik ...');
        });
    $('.fuel_type').select2({
        placeholder: 'Rodzaj paliwa',
        theme: 'classic',
        }).one('select2:open', function(e) {
            $('input.select2-search__field').prop('placeholder', 'Rodzaj paliwa ...');
        });
    $('.capacity').select2({
        placeholder: 'Pojemność silnika [cm3]',
        theme: 'classic',
        }).one('select2:open', function(e) {
            $('input.select2-search__field').prop('placeholder', 'Pojemność silnika [cm3] ...');
        });
    $('.mileage').select2({
        placeholder: 'Przebieg [km]',
        theme: 'classic',
            }).one('select2:open', function(e) {
                $('input.select2-search__field').prop('placeholder', 'Przebieg [km] ...');
        });
    $('.automatic').select2({
        placeholder: 'Skrzynia biegow',
        theme: 'classic',
        }).one('select2:open', function(e) {
            $('input.select2-search__field').prop('placeholder', 'Skrzynia biegów ...');
    });
    $('.wheel').select2({
        placeholder: 'Umieszczenie kierownicy', 
        theme: 'classic',              
        }).one('select2:open', function(e) {
            $('input.select2-search__field').prop('placeholder', 'Umieszczenie kierownicy ...');
    });  
    $('.damaged').select2({
        placeholder: 'Stan samochodu',
        theme: 'classic',               
        }).one('select2:open', function(e) {
            $('input.select2-search__field').prop('placeholder', 'Stan samochodu ...');
    });
    
        let year_select = document.getElementById('year');

        // chaining manufacturer and model
        let manufacturer_select = document.getElementById('manufacturer');
        let model_select = document.getElementById('model');
        
        manufacturer_select.onchange = function() {
            manufacturer = manufacturer_select.value;

            fetch('/models/' + manufacturer).then(function(response) {
                response.json().then(function(data) {
                    let optionHTML = '';

                    for (let model of data.models) {
                        optionHTML += '<option value="' + model.id + '">' + model.name + '</option>';
                    }
                   
                    model_select.innerHTML = optionHTML;

                });
            });
        };
        // end of chaining
    });
    