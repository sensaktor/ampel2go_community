



$(document).ready(function() {





    // JQuery code to be added in here.
    // $.ajax({
    //     url: 'testpage/',
    //     datatype: 'json',
    //     type: 'GET',
    //     sucess: function(data) {
    //         alert(data.name);
    //     }
    // });


    // $("#id_username").change(function () {
    //   console.log( $(this).val() );
    //   var username = $(this).val();
  
    //     $.ajax({
    //         url: '/ajax/validate_username/',
    //         data: {
    //         'username': username
    //         },
    //         dataType: 'json',
    //         success: function (data) {
    //         if (data.is_taken) {
    //             alert("A user with this username already exists.");
    //         }
    //         }
    //     });
    // });



    // function changebutton() {
    //     $.ajax({
    //         url: 'ajax/ajax_content',
    //         datatype: 'json',
    //         type: 'GET',
    //         data: { action: "add_car", id: "y" },
    //         success: function(data) {
    //             $.each(data.x, function(index, element) {
    //                 $("#result").html("<strong>"+data.x+"</strong>");
    //             });
    //         }
    //     });
    // };
});

// this works: 

    // $("#id_capacity").change(function () {
    //     console.log( $(this).val() );
    //     var username = $(this).val();

    //     $.ajax({
    //         url: 'ajax/ajax_content',
    //         datatype: 'json',
    //         type: 'GET',
    //         data: { action: "add_car", id: "y" },
    //         success: function(data) {
    //             $.each(data.x, function(index, element) {
    //                 $("#result").html("<strong>"+data.x+"</strong>");
    //             });
    //         }
    //     });
    // });




// $.ajax({
//     url: 'ajax/ajax_content',
//     datatype: 'json',
//     type: 'GET',
//     data: { action: "add_car", id: $car_id },
//     success: function(data){
//         // This will execute when where Django code returns a dictionary 
//         // called 'data' back to us.
//         $("#car").html("<strong>"+data.car+"</strong>");  
        
        
//         //("#result").html("<strong>"+{test: "ajax_content"}+"</strong>");
//         //$("#result").html("<strong>"+data.ajax_content+"</strong>");
        
//         //$.each(data.ajax_content, function(index, element) {
            
//             //$("#result").html("<strong>"+data.ajax_content+"</strong>");
//         });
//     }
// });
// });