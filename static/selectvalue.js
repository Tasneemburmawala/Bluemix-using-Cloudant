/**
 * Created by Tasneem on 2/15/2017.
 */

    alert("Hi");
    $('#selectedval').on('change', function () {
        alert("Hi");
        var filename = $(this).val();
        alert(filename);
        $.ajax({
            type: 'POST',
            url: '/filename/' + filename + '/'
        });
    });

