(function ($) {
    "use strict";

    // Spinner
    var spinner = function () {
        setTimeout(function () {
            if ($('#spinner').length > 0) {
                $('#spinner').removeClass('show');
            }
        }, 1);
    };
    spinner(0);


    // Fixed Navbar
    $(window).scroll(function () {
        if ($(window).width() < 992) {
            if ($(this).scrollTop() > 55) {
                $('.fixed-top').addClass('shadow');
            } else {
                $('.fixed-top').removeClass('shadow');
            }
        } else {
            if ($(this).scrollTop() > 55) {
                $('.fixed-top').addClass('shadow').css('top', -55);
            } else {
                $('.fixed-top').removeClass('shadow').css('top', 0);
            }
        }
    });


    // Back to top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 300) {
            $('.back-to-top').fadeIn('slow');
        } else {
            $('.back-to-top').fadeOut('slow');
        }
    });
    $('.back-to-top').click(function () {
        $('html, body').animate({ scrollTop: 0 }, 1500, 'easeInOutExpo');
        return false;
    });


    // Testimonial carousel
    $(".testimonial-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 2000,
        center: false,
        dots: true,
        loop: true,
        margin: 25,
        nav: true,
        navText: [
            '<i class="bi bi-arrow-left"></i>',
            '<i class="bi bi-arrow-right"></i>'
        ],
        responsiveClass: true,
        responsive: {
            0: {
                items: 1
            },
            576: {
                items: 1
            },
            768: {
                items: 1
            },
            992: {
                items: 2
            },
            1200: {
                items: 2
            }
        }
    });


    // vegetable carousel
    $(".vegetable-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1500,
        center: false,
        dots: true,
        loop: true,
        margin: 25,
        nav: true,
        navText: [
            '<i class="bi bi-arrow-left"></i>',
            '<i class="bi bi-arrow-right"></i>'
        ],
        responsiveClass: true,
        responsive: {
            0: {
                items: 1
            },
            576: {
                items: 1
            },
            768: {
                items: 2
            },
            992: {
                items: 3
            },
            1200: {
                items: 4
            }
        }
    });


    // Modal Video
    $(document).ready(function () {
        var $videoSrc;
        $('.btn-play').click(function () {
            $videoSrc = $(this).data("src");
        });
        console.log($videoSrc);

        $('#videoModal').on('shown.bs.modal', function (e) {
            $("#video").attr('src', $videoSrc + "?autoplay=1&amp;modestbranding=1&amp;showinfo=0");
        })

        $('#videoModal').on('hide.bs.modal', function (e) {
            $("#video").attr('src', $videoSrc);
        })
    });



    // Product Quantity
    $('.quantity button').on('click', function () {
        var button = $(this);
        var oldValue = button.parent().parent().find('input').val();
        if (button.hasClass('btn-plus')) {
            var newVal = parseFloat(oldValue) + 1;
        } else {
            if (oldValue > 0) {
                var newVal = parseFloat(oldValue) - 1;
            } else {
                newVal = 0;
            }
        }
        button.parent().parent().find('input').val(newVal);
    });

})(jQuery);

function login() {
    const loginUsername = document.getElementById("loginUsername").value;
    const loginPassword = document.getElementById("loginPassword").value;
    const securityKey = document.getElementById("securityKey").value;

    if (loginUsername == "") {
        alert("Please enter a valid username");
        return;
    }
    if (loginPassword == "") {
        alert("Please enter a valid password");
        return;
    }

    if (securityKey == ""){
        alert("Please enter a valid security key")
        return;
    }

    axios({
        method: 'post',
        url: `login`,
        headers: {
            'Content-Type': 'application/json',
        },
        data: {
            "loginUsername": loginUsername,
            "loginPassword": loginPassword,
            "securityKey": securityKey
        }
    })
        .then(function (response) {
            if (response.data.startsWith("ERROR:")) {
                console.log(response.data)
                alert("An error occured while logging you in. Please try again.")
                return;
            }
            else if (response.data.startsWith("UERROR:")) {
                console.log(response.data)
                alert(response.data.substring("UERROR: ".length))
                return;
            }
            console.log(response.data)
            document.getElementById("loginButton").innerHTML = "Logging you in..."
            setTimeout(function () {
                window.location.href = "/editor";
            }, 2000);
        })
        .catch(function (error) {
            console.error('Error logging in:', error);
        });
}

function logout(){
    axios({
        method: 'post',
        url: `logout`,
        headers: {
            'Content-Type': 'application/json',
        }
    })
        .then(function (response) {
            if (response.data.startsWith("ERROR:")) {
                console.log(response.data)
                alert("An error occured while logging out. Please try again.")
                return;
            }
            else if (response.data.startsWith("UERROR:")) {
                console.log(response.data)
                alert(response.data.substring("UERROR: ".length))
                return;
            }
            console.log(response.data)
            document.getElementById("logoutButton").innerHTML = "Logging out..."
            setTimeout(function () {
                window.location.href = "/admin";
            }, 2000);
        })
        .catch(function (error) {
            console.error('Error logging in:', error);
        });
}

var PostIDtoEdit = null
function setPostIDtoEdit(PostID){
    PostIDtoEdit = PostID
}

function submitEdits(index){
    const editedTitle = document.getElementById('editTitle' + index).value;
    const editedDescription = document.getElementById('editDescription' + index).value;

    if (editedTitle == ""){
        document.getElementById("editErrorMessage").innerHTML = "Title cannot be empty!";
        return;
    }
    if (editedDescription == ""){
        document.getElementById("editErrorMessage").innerHTML = "Description cannot be empty!";
        return;
    }

    axios({
        method: 'post',
        url: `editPost`,
        headers: {
            'Content-Type': 'application/json',
        },
        data: {
            "editedTitle": editedTitle,
            "editedDescription": editedDescription,
            "editPostID": PostIDtoEdit
        }
    })
        .then(function (response) {
            if (response.data.startsWith("ERROR:")) {
                console.log(response.data)
                alert("An error occured while editing post. Please try again.")
                return;
            }
            else if (response.data.startsWith("UERROR:")) {
                console.log(response.data)
                alert(response.data.substring("UERROR: ".length))
                return;
            }
            console.log(response.data)
            window.location.reload();
        })
        .catch(function (error) {
            console.error('Error editing post:', error);
        });
    
}

function deletePost(postIDtoDelete){
    axios({
        method: 'post',
        url: `deletePost`,
        headers: {
            'Content-Type': 'application/json',
        },
        data: {
            "postID": postIDtoDelete
        }
    })
        .then(function (response) {
            if (response.data.startsWith("ERROR:")) {
                console.log(response.data)
                alert("An error occured while deleting post. Please try again.")
                return;
            }
            else if (response.data.startsWith("UERROR:")) {
                console.log(response.data)
                alert(response.data.substring("UERROR: ".length))
                return;
            }
            console.log(response.data)
            window.location.reload();
        })
        .catch(function (error) {
            console.error('Error deleting post:', error);
        });
}

function submitPost(){
    const postTitle = document.getElementById("postTitle").value;
    const postDescription = document.getElementById("postDescription").value;

    if (postTitle == ""){
        document.getElementById("createErrorMessage").innerHTML = "Title cannot be empty!";
        return;
    }
    if (postDescription == ""){
        document.getElementById("createErrorMessage").innerHTML = "Description cannot be empty!";
        return;
    }

    axios({
        method: 'post',
        url: `submitPost`,
        headers: {
            'Content-Type': 'application/json',
        },
        data: {
            "postTitle": postTitle,
            "postDescription": postDescription
        }
    })
        .then(function (response) {
            if (response.data.startsWith("ERROR:")) {
                console.log(response.data)
                alert("An error occured while submitting post. Please try again.")
                return;
            }
            else if (response.data.startsWith("UERROR:")) {
                console.log(response.data)
                alert(response.data.substring("UERROR: ".length))
                return;
            }
            console.log(response.data)
            window.location.reload();
        })
        .catch(function (error) {
            console.error('Error submitting post:', error);
        });
}

