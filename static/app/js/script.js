
const selectImage = document.querySelector('.select-image');
const inputFile = document.querySelector('#file');
const imgArea = document.querySelector('.img-area');

// Trigger click event on file input when "Select Image" button is clicked
selectImage.addEventListener('click', function () {
  console.log("CLICKEDD")
    inputFile.click();
});

// Handle image selection from file input
inputFile.addEventListener('change', function () {
    const image = this.files[0];
    if (image.size < 2000000) { // Check if image size is less than 2MB
        const reader = new FileReader();
        reader.onload = () => {
            const allImg = imgArea.querySelectorAll('img');
            allImg.forEach(item => item.remove());
            const imgUrl = reader.result;
            const img = document.createElement('img');
            img.src = imgUrl;
            imgArea.appendChild(img);
            imgArea.classList.add('active');
            imgArea.dataset.img = image.name;
        };
        reader.readAsDataURL(image);
    } else {
        alert("Image size more than 2MB");
    }
});



