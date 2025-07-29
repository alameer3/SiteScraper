$likes = $.cookie('likes_' + decodeURI(window.location.pathname));
$dislikes = $.cookie('dislikes_' + decodeURI(window.location.pathname));
$(document).ready(function () {
  var $app = $('#page_app'),
    $id = $('#page_id');
  if ($app.length && $id.length) {
    $.ajax({
      type: "GET",
      url: site_url + '/v/' + $app.val() + '/' + $id.val(),
    });
  }
  $(document).on('submit', 'form.ajax', function ($e) {
    $e.preventDefault();
    submit_form($(this));
  });
  $('form.validate').validate();
});

function dd($var) {
  console.log($var)
}

function submit_form($form) {
  if ($form.hasClass('validate') && $form.valid() || !$form.hasClass('validate')) {
    $.ajax({
      type: $form.attr('method'),
      url: $form.attr('action'),
      data: $form.serialize(),
      success: function ($response) {
        if ($response.status == 'success')
          $form[0].reset();
        $.fancybox.close();
        swal($response.msg, {
          buttons: {
            cancel: "اغلاق",
          },
        });
      },
      error: function ($response) {
        $.each($response.responseJSON.errors, function ($name, $error) {
          alert($error[0]);
          // swal($error[0], {
          //   buttons: {
          //     cancel: "اغلاق",
          //   },
          // });
          return false;
        });
      },
      dataType: 'JSON'
    });
  }
}

$(document).on('submit', 'form.comment', function ($e) {
  $e.preventDefault()
  $form = $(this);
  if ($form.find('textarea').val()) {
    $.ajax({
      type: $form.attr('method'),
      url: $form.attr('action'),
      data: $form.serialize(),
      success: function ($response) {
        if ($response.status == 'success') {
          $form[0].reset();
          $('<div class="comment-item d-flex no-gutters mb-4">\n' +
            '                    <div class="col-auto ml-4">\n' +
            '                      <img src="' + img($response.comment.commenter.img, '50x50') + '" class="img-fluid rounded-circle" alt="user avatar" style="border: 1px solid #e7e7e7">\n' +
            '                    </div>\n' +
            '                    <div class="col">\n' +
            '                      <div class="comment-details bg-primary2 rounded p-3">\n' +
            '                        <p class="text-white m-0">' + $response.comment.text + '</p>\n' +
            '                        <div class="d-flex align-items-center mt-2">\n' +
            '                          <h3 class="username font-size-14 m-0 text-muted">' + $response.comment.commenter.name + '</h3>\n' +
            '                                                  </div>\n' +
            '                      </div>\n' +
            '                    </div>\n' +
            '                  </div>').insertAfter('.comments-widget')
        } else {
          swal($response.msg);
        }
      },
      error: function ($response) {
        $.each($response.responseJSON.errors, function ($name, $error) {
          swal($error[0], {
            buttons: {
              cancel: "اغلاق",
            },
          });
          return false;
        });
      },
      dataType: 'JSON'
    });
  }
});

function img($path, $d) {
  if ($d) {
    return LibraryServerUrl + 'thumb/' + $d + '/' + $path;
  } else
    return LibraryServerUrl + 'thumb/' + $path;
}

if (($.cookie('authenticated') !== undefined) && ($.cookie('user') !== undefined)) {
  $('.private').removeClass('hide');
  $('.public').addClass('hide');
  $user = JSON.parse($.cookie('user'));
  $('.user-panel .login-panel .username').text($user.name);
  $('.user-panel .login-panel img').attr('src', img($user.img, '32x32'));
  $('.comments-widget .comments-form img').attr('src', img($user.img, '50x50'));
  $('.comments-widget .comments-form .username').text($user.name);
  favorite_movies = $.cookie('favorite_movies') ? JSON.parse($.cookie('favorite_movies')) : [];
  favorite_series = $.cookie('favorite_series') ? JSON.parse($.cookie('favorite_series')) : [];
  favorite_shows = $.cookie('favorite_shows') ? JSON.parse($.cookie('favorite_shows')) : [];
  favorite_games = $.cookie('favorite_games') ? JSON.parse($.cookie('favorite_games')) : [];
  favorite_programs = $.cookie('favorite_programs') ? JSON.parse($.cookie('favorite_programs')) : [];
  favorite_mix = $.cookie('favorite_mix') ? JSON.parse($.cookie('favorite_mix')) : [];
  $.each(favorite_movies, function (k, id) {
    $('.add-to-fav[data-type="movie"][data-id="' + id + '"]').addClass('added');
  });
  $.each(favorite_series, function (k, id) {
    $('.add-to-fav[data-type="series"][data-id="' + id + '"]').addClass('added');
  });
  $.each(favorite_shows, function (k, id) {
    $('.add-to-fav[data-type="show"][data-id="' + id + '"]').addClass('added');
  });
  $.each(favorite_games, function (k, id) {
    $('.add-to-fav[data-type="game"][data-id="' + id + '"]').addClass('added');
  });
  $.each(favorite_programs, function (k, id) {
    $('.add-to-fav[data-type="program"][data-id="' + id + '"]').addClass('added');
  });
  $.each(favorite_mix, function (k, id) {
    $('.add-to-fav[data-type="mix"][data-id="' + id + '"]').addClass('added');
  });
}
$(document).on('click', '.add-to-fav', function (e) {
  e.preventDefault();
  $this = $(this);
  $this.toggleClass('added');
  $.ajax({
    type: "POST",
    url: site_url + '/favorite',
    data: {id: $this.data('id'), type: $this.data('type')},
    dataType: 'JSON'
  });
});
$('.share .facebook').on('click', function ($e) {
  $e.preventDefault();
  window.open('https://www.facebook.com/sharer/sharer.php?u=' + window.location, '_blank');
});
$('.share .twitter').on('click', function ($e) {
  $e.preventDefault();
  window.open('http://twitter.com/share?url=' + window.location, '_blank');
});
$('.share .messenger').on('click', function ($e) {
  $e.preventDefault();
  window.open('https://www.facebook.com/sharer/sharer.php?u=' + window.location, '_blank');
});
$('.share .whatsapp').on('click', function ($e) {
  $e.preventDefault();
  window.open('https://api.whatsapp.com/send?text=' + window.location, '_blank');
});
$('.like').on('click', function ($e) {
  $e.preventDefault();
  if ($.cookie('dislikes_' + decodeURI(window.location.pathname)) == undefined && ($.cookie('likes_' + decodeURI(window.location.pathname)) == undefined)) {
    $this = $(this),
      $number = parseInt($this.find('.number').text()) + 1;
    $this.addClass('active').find('.number').text($number);
    $.cookie('likes_' + decodeURI(window.location.pathname), $number);
    $.ajax({
      type: "POST",
      url: $site_url + 'like',
      dataType: 'JSON'
    });
  }
});
$('.unlike').on('click', function ($e) {
  $e.preventDefault();
  if ($.cookie('dislikes_' + decodeURI(window.location.pathname)) == undefined && ($.cookie('likes_' + decodeURI(window.location.pathname)) == undefined)) {
    $this = $(this),
      $number = parseInt($this.find('.number').text()) + 1;
    $this.addClass('active').find('.number').text($number);
    $.cookie('dislikes_' + decodeURI(window.location.pathname), $number);
    $.ajax({
      type: "POST",
      url: $site_url + 'dislike',
      dataType: 'JSON'
    });
  }
});
if ($likes != undefined) {
  $('.like .number').text($likes);
}
if ($dislikes != undefined) {
  $('.unlike .number').text($dislikes);
}
$('.tab-content.quality').each(function () {
  var $rand = Math.floor(Math.random() * $(this).find('.duplicated.d-none').length) + 0;
  $(this).find('.duplicated.d-none:eq(' + $rand + ')').removeClass('d-none');
});
var view_more = 1;
while (view_more <= 6) {
  var $rand = Math.floor(Math.random() * $('.widget-4.more .widget-body .row > .d-none').length) + 0;
  $('.widget-4.more .widget-body .row > .d-none:eq(' + $rand + ')').removeClass('d-none');
  view_more++;
}