var cityInfo1 = {};
    var cityInfo2 = {};
    var cities = [cityInfo1, cityInfo2];
    var previousCity
    var winningCity

    $(document).ready(function(){
        $('#results-table').hide();
        $('#final-decision-form').hide();
        $("#algo-result").hide();
        $("#component-weights").hide();
        $(".loader").hide()

        $("#preference-form").on("submit", getData);
        $("#pp-choice").on("click", exploreCity);
        $(".importance-slider").on("change", reCalculate);

        });

    function prepDom() {
        $("#gather-data-button").hide();
        $("#city-specific-pref").hide();
        $("#travel-dates").hide();
        $("#departure-dropdown").hide();
        $("#temp-selectors").hide();
        $('#results-table').show();
        $('#final-decision-form').show();
        $('#component-weights').show()
        $(".photo-carousel").hide();
        $("#general-pref").hide()
        $(".city-header").hide()

    }

    function determineDestination(cities) {
        var cityInfo1 = cities[0];
        var cityInfo2 = cities[1];

        var idealTemp = $("input:radio[name=ideal-temp]:checked").val();

        var costWeight = parseInt($("#cost-weight").val());
        var foodWeight = parseInt($("#food-weight").val());
        var weatherWeight = parseInt($("#weather-weight").val());
        var totalWeight = costWeight + foodWeight + weatherWeight;

        var flightDelta = (cityInfo1.airfare - cityInfo2.airfare)/(cityInfo1.airfare);
        var colDelta = (cityInfo1.costOfLiving - cityInfo2.costOfLiving)/(cityInfo1.costOfLiving);

        var weatherDeltaCity1 = cityInfo1.weather - idealTemp;
        var weatherDeltaCity2 = cityInfo2.weather - idealTemp;
        var weatherDelta = (weatherDeltaCity1 - weatherDeltaCity2)/weatherDeltaCity1;

        var wowDelta = (cityInfo1.wow - cityInfo2.wow)/cityInfo1.wow;


        if (cityInfo1.food > 0) {
            var starDelta = (cityInfo1.food - cityInfo2.food)/cityInfo1.food;
        }
        else if (cityInfo2.food > 0) {
            var starDelta = -1;
        }

        else {
            var starDelta = 0;
        }

        var dataDelta = (foodWeight/totalWeight)*starDelta -
                        (costWeight*0.5/totalWeight)*colDelta -
                        (costWeight*0.5/totalWeight)*flightDelta - 
                        (weatherWeight/totalWeight)*weatherDelta
        
        if (dataDelta + wowDelta > 0) {
            winningCity = cityInfo1;
        }

        else if (dataDelta + wowDelta < 0) {
            winningCity = cityInfo2;
        }

       else { 
            var trips = [cityInfo1, cityInfo2];
            winningCity = trips[Math.floor(Math.random()*trips.length)];
        }

        if (flightDelta > 0) { $("#flight-2").attr("style", "color:#66CDAA")}
        else if (flightDelta < 0) {$("#flight-1").attr("style", "color:#66CDAA")}

        if (weatherDelta > 0) { $("#weather-2").attr("style", "color:#66CDAA")}
        else if (weatherDelta < 0) {$("#weather-1").attr("style", "color:#66CDAA")}

        if (starDelta > 0) { $("#food-1").attr("style", "color:#66CDAA")}
        else if (starDelta < 0) {$("#food-2").attr("style", "color:#66CDAA")}

        if (colDelta > 0) { $("#col-2").attr("style", "color:#66CDAA")}
        else if (colDelta < 0) {$("#col-1").attr("style", "color:#66CDAA")}

        if (wowDelta > 0) { $("#wow-1").attr("style", "color:#66CDAA")}
        else if (wowDelta < 0) {$("#wow-2").attr("style", "color:#66CDAA")}

        $("#pp-choice").html('Explore ' + winningCity.city);
        $("#pp-choice-text").html("Pensive Passport's algorithm has selected: " + 
                                    "<span class='tertiary-color'>" + 
                                    "<strong>" + winningCity.city + "</strong></span>");
        $("#pp-choice").data("city", winningCity.city);
        $("#pp-choice").data("country", winningCity.country);
        $("#pp-choice").data("cityId", winningCity.cityId);
        $("#algo-result").show();

    }          

    function getData(evt){   
        evt.preventDefault();
        prepDom();
        
        var apiResponses = 0;

        for (i=1; i < cities.length + 1; i++) {loopCities(i)}
        
        function loopCities(i) {
            var cityInfo = cities[i-1];
            $("#wow-"+i).html($("#wow-input-"+i).val());
            cityInfo.wow = $("#wow-input-"+i).val()

            var url = '/get-city' + i + '-data?airport-'+i+'='+ $("#airport-"+i).val();
            $.get(url, function (result) {                
                cityInfo.city = result.city;
                cityInfo.cityId = result.cityId;
                cityInfo.country = result.country;
                cityInfo.food = parseInt(result.food);
                cityInfo.food = getNum(cityInfo.food);
                cityInfo.costOfLiving = parseInt(result.costOfLiving);
                $('#food-'+i).html(cityInfo.food + ' ' + 
                                    "<img class='michelin-star' src='/static/images/michelinstar.jpg'>");
                $('#col-'+i).html(cityInfo.costOfLiving);
                
                }
            );
                        
            $.post("/get-flight" + i,
                {depart_date: $("#depart-date").val(), 
                return_date: $("#return-date").val(), 
                origin: $("#departure-airport").val(), 
                destination: $("#airport-"+i).val()},
                function (result) {
                    $('#flight-'+i).html("$" + result.airfare);
                    cityInfo.airfare = result.airfare;
                    apiResponses ++;
                    if (apiResponses===4) {
                        $.post('/store-trips',
                            {'trip1':JSON.stringify(cities[0]), 
                            'trip2':JSON.stringify(cities[1])}, 
                            function(result) {});
                        determineDestination(cities)};
                }
            );

            $.post("/get-weather" + i,
                {depart_date: $("#depart-date").val(), 
                destination: $("#airport-"+i).val()},
                function (result) {
                    $('#weather-'+i).html(result.low + " - " + result.high + " F");
                    cityInfo.weather = (parseInt(result.low) + parseInt(result.high))/2;
                    apiResponses ++;
                    if (apiResponses===4) {
                        $.post('/store-trips',
                            {'trip1':JSON.stringify(cities[0]),
                            'trip2':JSON.stringify(cities[1])},
                            function(result) {});
                        determineDestination(cities)};
                }
            );
        }

    }

    function reCalculate() {
        previousCity = winningCity.city;
        
        determineDestination(cities);
        if (previousCity === winningCity.city) {
            $("#pp-choice-text").html("After recalculation, Pensive Passport " + 
                                        "<strong>still</strong> chooses " + winningCity.city + "!");
        }

        else {$("#pp-choice-text").html("After recalculation, Pensive Passport now selects " + 
                                        "<span style='color:red'>" + winningCity.city + "</span>!");
        } 
        }        

    function exploreCity(evt) {
        $(".loader").fadeIn("slow");
        var cityId = $(this).data("cityId");

        window.location = "http://localhost:5000/results?city_id=" + cityId;

    }

    function getNum(val)
        {
           if (isNaN(val)) 
             return 0;
           else
             return val;
        }

