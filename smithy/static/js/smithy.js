/**
 * Initialize CodeMirror. Also hide the body input
 * field when the METHOD is set to GET.
 */
(function ($) {
    var METHOD_GET = 'GET';
    $(document).on("DOMContentLoaded", function(event) {
        var row = document.querySelector(".form-row.field-body");

        var code = document.getElementById("id_body");
        var method = document.getElementById("id_method");

        function toggle_body() {
            var m = method.value;
            if (m === METHOD_GET) {
                row.style.display = 'none';
            } else {
                row.style.display = 'block';
            }
        }

        window.editor = CodeMirror.fromTextArea(code, {
            mode: 'django',
            lineNumbers: true
        });

        $(method).on('change', toggle_body);
        toggle_body();

    });
})(django.jQuery);


/**
 * Switch to password inputs when the field name
 * contains terms like "key" or "pass"
 */
(function ($) {
    function set_type(id, type) {
        $('#' + id).attr("type", type);
    }
    function update_listeners() {
        document.querySelectorAll("#requestblueprint_form .module .form-row .field-name > input[type='text']").forEach(function (field) {
            field.addEventListener('change', function ($e) {
                var name = $e.target.value;
                var id = $e.target.id;
                var target_id = id.replace(/-name$/, '-value');
                if (/pass|key|secret/.test(name)) {
                    set_type(target_id, 'password');
                } else {
                    set_type(target_id, 'text');
                }
            })
        })
    }

    $(document).on("DOMContentLoaded", update_listeners);
    $(document).on("formset:added", update_listeners);
})(django.jQuery);
