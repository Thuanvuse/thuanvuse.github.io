window.addEventListener("scroll", function () {
    let navbar = document.querySelector(".custom-navbar");

    if (window.scrollY > 50) {
        navbar.classList.add("bg-dark", "shadow");
        navbar.classList.remove("mt-5"); // Xóa mt-5 khi cuộn xuống
    } else {
        navbar.classList.remove("bg-dark", "shadow");
        navbar.classList.add("mt-5"); // Thêm lại mt-5 khi cuộn lên
    }
});
