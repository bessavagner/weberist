(vendor, renderer) => {
// Override the Worker constructor to intercept worker creation
(function() {
    const originalWorker = window.Worker;

    // Custom worker interceptor
    window.Worker = function(scriptURL) {
        const worker = new originalWorker(scriptURL);
        
        // Override the onmessage method to intercept the worker messages
        const originalOnMessage = worker.onmessage;
        
        worker.onmessage = function(event) {
            try {
                // Intercept and modify the worker data before it's processed
                if (event.data.webGLVendor) {
                    event.data.webGLVendor = vendor || 'Intel Inc.';
                }
                if (event.data.webGLRenderer) {
                    event.data.webGLRenderer = renderer || 'Intel Iris OpenGL Engine';
                }
                if (event.data.hardwareConcurrency) {
                    event.data.hardwareConcurrency = 8;
                }
                
                // Call the original onmessage handler if it exists
                if (originalOnMessage) {
                    originalOnMessage.call(this, event);
                }
            } catch (err) {
                console.error('Error intercepting worker data:', err);
            }
        };

        return worker;
    };
})();

// // Optional: Override any other main thread properties that need to match the worker
// function overrideMainThreadValues() {
//     Object.defineProperty(navigator, 'hardwareConcurrency', {
//         get: function() { return 8; }
//     });

//     const canvas = document.createElement('canvas');
//     const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');

//     if (gl) {
//         const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
//         if (debugInfo) {
//             Object.defineProperty(gl, 'getParameter', {
//                 value: function(param) {
//                     if (param === debugInfo.UNMASKED_VENDOR_WEBGL) {
//                         return vendor || 'Intel Inc.';
//                     }
//                     if (param === debugInfo.UNMASKED_RENDERER_WEBGL) {
//                         return renderer || 'Intel Iris OpenGL Engine';
//                     }
//                     return gl.getParameter(param);
//                 }
//             });
//         }
//     }
// }

// overrideMainThreadValues();


}
