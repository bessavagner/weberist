() => {
    function handleKeys(pattern, action) {
        Object.keys(window).forEach(function(key) {
            if (key.match(pattern)) {
                action(key);
            }
        });
    }
    
    // Example action to delete keys
    function deleteAction(key) {
        delete window[key];
    }
    
    // Regular expression pattern for the keys (any prefix followed by the suffix)
    const keyPattern = /.*_(Array|Object|Promise|Proxy|Symbol|JSON)$/;
    
    // Add event listener to handle keys on DOMContentLoaded
    document.addEventListener('DOMContentLoaded', function() {
        handleKeys(keyPattern, deleteAction);
    });
}