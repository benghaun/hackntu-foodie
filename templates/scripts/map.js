var infowindow;
var map;
var reddot = {url: "https://maps.google.com/mapfiles/ms/icons/red-dot.png"};
var bluedot = {url: "https://maps.google.com/mapfiles/ms/icons/blue-dot.png"};

function addMarker (markerarray,marker){
    markerarray[markerarray.length]=marker;
};

function createMarker(string,latlng,pin){
    var marker=new google.maps.Marker({position:latlng,map:map,icon:pin});
    google.maps.event.addListener(marker,"click",function(){
        if(infowindow)infowindow.close();
        infowindow=new google.maps.InfoWindow({content:string});
        infowindow.open(map,marker);
    });
    return marker;
};

function initMap(){
    var singapore=new google.maps.LatLng(1.35,103.82);
    var options={zoom:11,center:singapore};
    map=new google.maps.Map(document.getElementById("map"),options);
    map.discmarkers=new Array();
    map.nearbymarkers = new Array();

    $.ajax({
        url: "/getdeals",
        method: "GET",
        dataType: "json",
        data: {},
        complete: function(xhr, status) {},
        success: function(data, status, xhr) {
            for(var i=0;i<data.length;i++){
                var card = new Object();
                card.name = data[i].name;
                card.enddate = data[i].enddate;
                card.timeinfo = (data[i].timeinfo)? data[i].timeinfo:'';
                card.timeinfo = '<br><br>'+card.timeinfo;
                card.latlongs = data[i].latlongs;
                var contentString = '<div id="infoview">'+
                    '<p><b>'+ card.name + '</b><br>' +
                    'Until '+ card.enddate.substring(0, card.enddate.length-13) +
                    card.timeinfo +
                    '</p></div>'
                for(var j=0;j<card.latlongs.length;j++){
                    var latlng=new google.maps.LatLng(card.latlongs[j][0],card.latlongs[j][1]);
                    addMarker(map.discmarkers,createMarker(contentString,latlng,reddot));
                }
            }
        }
    });
};

$(document).ready(function() {
    $("#zoomarea").click(function() {
        var searchBtn = document.getElementById('zoomarea');
        var randomBtn = document.getElementById('randomchoice')
        randomBtn.disabled = true;
        searchBtn.innerHTML = "Loading...";
        searchBtn.disabled = true;
        var area = $("#zoominput").val();
        $("#zoominput").blur();
        var urlString = "/viewport?search=" + area;
        for(var i=0;i<map.nearbymarkers.length;i++){
            map.nearbymarkers[i].setMap(null);
        }
        map.nearbymarkers = new Array();
        $.ajax({
            url: urlString,
            method: "GET",
            dataType: "json",
            data: {},
            complete: function(xhr, status) {},
            success: function(data, status, xhr) {
                var bounds = new google.maps.LatLngBounds(data.results.southwest,data.results.northeast)
                map.fitBounds(bounds);
                for(var j=0;j<data.results.nearby.length;j++){
                    var contentString = '<div id="infoview">'+
                        '<p><b>'+ data.results.nearby[j].name + '</b><br>' +
                        '\u2B50 '+ data.results.nearby[j].rating +
                        '</p></div>'
                    var latlng=new google.maps.LatLng(data.results.nearby[j].latlongs[0][0],data.results.nearby[j].latlongs[0][1]);
                    addMarker(map.nearbymarkers,createMarker(contentString,latlng,bluedot));
                }
                map.chosen = data.results.chosen;
                searchBtn.innerHTML = "Search";
                searchBtn.disabled = false;
                randomBtn.disabled = false;
            }
        });
    });
    
    $("#zoominput").on("keydown", function(e) { 
        if(e.keyCode == 13)
            $("#zoomarea").click() 
    });

    $("#randomchoice").click(function() {
        var searchBtn = document.getElementById('zoomarea');
        var randomBtn = document.getElementById('randomchoice')
        randomBtn.disabled = true;
        randomBtn.innerHTML = "Loading...";
        searchBtn.disabled = true;
        var area = $("#zoominput").val();
        var urlString = "/viewport?search=" + area;
        for(var i=0;i<map.nearbymarkers.length;i++){
            map.nearbymarkers[i].setMap(null);
        }
        map.nearbymarkers = new Array();
        $.ajax({
            url: urlString,
            method: "GET",
            dataType: "json",
            data: {},
            complete: function(xhr, status) {},
            success: function(data, status, xhr) {
                var bounds = new google.maps.LatLngBounds(data.results.southwest,data.results.northeast)
                map.fitBounds(bounds);
                var contentString = '<div id="infoview">'+
                    '<p><b>'+ data.results.chosen.name + '</b><br>' +
                    '\u2B50 '+ data.results.chosen.rating +
                    '</p></div>'
                var latlng=new google.maps.LatLng(data.results.chosen.latlongs[0][0],data.results.chosen.latlongs[0][1]);
                addMarker(map.nearbymarkers,createMarker(contentString,latlng,bluedot));
                randomBtn.disabled = false;
                randomBtn.innerHTML = "Anything";
            }
        });
    });
}); 