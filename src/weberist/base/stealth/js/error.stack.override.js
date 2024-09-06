() => {
    // Backup original Object.defineProperty
    const originalDefineProperty = Object.defineProperty;

    // Override Object.defineProperty for the Error stack check
    Object.defineProperty = function(obj, prop, descriptor) {
        // Check if it's modifying Error.stack
        if (obj instanceof Error && prop === 'stack') {
            // If trying to define a getter that modifies fingerprintWorker.cdp, ignore it
            if (descriptor.get) {
                // Provide a harmless stack getter instead
                descriptor.get = function() {
                    return ''; // Return an empty string to simulate the stack but don't modify cdp
                };
            }
        }
        // Call the original Object.defineProperty
        return originalDefineProperty.call(Object, obj, prop, descriptor);
    };

    // The rest of your code remains unaffected

}