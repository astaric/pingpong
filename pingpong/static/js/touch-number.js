$.fn.create_touch_targets = function (options) {
    this.each(function () {
        console.log(options);
        options = options || {};
        console.log(options);
        var $this = $(this);
        var name = this.name;
        var value = this.value;

        var touch_targets = '';
        for (var val = options.min_value; val <= options.max_value; val++) {
            var id = name + '-' + val;
            var selected = (value === '' + val) ? ' checked' : '';
            if (value) {
                $this.parent().addClass('selected');
            }

            touch_targets +=
                '<input type="radio" id="' + id + '" name="' + name + '" value="' + val + '"' + selected + '>' +
                    '<label for="' + id + '">' + val + '</label>';
        }

        $this.replaceWith(touch_targets);
    });
    return this
};
