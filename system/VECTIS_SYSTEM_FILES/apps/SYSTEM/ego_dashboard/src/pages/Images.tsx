function Images() {
  const imagePaths = [
    "/images/IMG_2217.PNG",
    "/images/IMG_2219.PNG",
    "/images/IMG_2220.PNG",
    "/images/IMG_2221.PNG",
    "/images/IMG_2222.PNG",
  ];

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold mb-4">Image Gallery</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {imagePaths.map((path, index) => (
          <div key={index} className="overflow-hidden rounded-lg shadow-lg">
            <img 
              src={path} 
              alt={`Gallery Image ${index + 1}`} 
              className="w-full h-48 object-cover transform hover:scale-105 transition-transform duration-300" 
            />
          </div>
        ))}
      </div>
      <p className="mt-4 text-sm text-gray-400">
        Note: Only a subset of images are shown for demonstration purposes.
      </p>
    </div>
  );
}

export default Images;