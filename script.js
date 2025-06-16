class KioskApp {
    constructor() {
        this.currentScreen = 'welcome-screen';
        this.inactivityTimer = null;
        this.inactivityTimeout = 30000; // 30 seconds
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.startInactivityTimer();
        this.showScreen('welcome-screen');
    }

    setupEventListeners() {
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
        
        events.forEach(event => {
            document.addEventListener(event, () => {
                this.resetInactivityTimer();
            }, true);
        });

        document.addEventListener('contextmenu', (e) => {
            e.preventDefault();
        });

        document.addEventListener('selectstart', (e) => {
            e.preventDefault();
        });

        document.addEventListener('dragstart', (e) => {
            e.preventDefault();
        });

        document.addEventListener('keydown', (e) => {
            if (e.key === 'F11' || 
                (e.altKey && e.key === 'F4') ||
                (e.ctrlKey && e.key === 'w') ||
                (e.ctrlKey && e.key === 'W')) {
                e.preventDefault();
            }
        });
    }

    showScreen(screenId) {
        const screens = document.querySelectorAll('.screen');
        screens.forEach(screen => {
            screen.classList.remove('active');
        });

        const targetScreen = document.getElementById(screenId);
        if (targetScreen) {
            targetScreen.classList.add('active');
            this.currentScreen = screenId;
        }

        this.resetInactivityTimer();
    }

    startInactivityTimer() {
        this.inactivityTimer = setTimeout(() => {
            this.returnToWelcome();
        }, this.inactivityTimeout);
    }

    resetInactivityTimer() {
        if (this.inactivityTimer) {
            clearTimeout(this.inactivityTimer);
        }
        this.startInactivityTimer();
    }

    returnToWelcome() {
        this.showScreen('welcome-screen');
        
        const welcomeScreen = document.getElementById('welcome-screen');
        welcomeScreen.style.opacity = '0';
        setTimeout(() => {
            welcomeScreen.style.opacity = '1';
        }, 100);
    }

    showMainMenu() {
        this.showScreen('main-menu');
    }

    showPage(pageId) {
        this.showScreen(pageId);
    }

    goHome() {
        this.showScreen('welcome-screen');
    }
}

let kioskApp;

function showMainMenu() {
    kioskApp.showMainMenu();
}

function showPage(pageId) {
    kioskApp.showPage(pageId);
}

function goHome() {
    kioskApp.goHome();
}

function addTouchFeedback() {
    const buttons = document.querySelectorAll('.touch-button');
    
    buttons.forEach(button => {
        button.addEventListener('touchstart', function(e) {
            this.style.transform = 'scale(0.95)';
            this.style.transition = 'transform 0.1s ease';
        });

        button.addEventListener('touchend', function(e) {
            setTimeout(() => {
                this.style.transform = '';
                this.style.transition = 'all 0.3s ease';
            }, 100);
        });

        button.addEventListener('mousedown', function(e) {
            this.style.transform = 'scale(0.95)';
        });

        button.addEventListener('mouseup', function(e) {
            setTimeout(() => {
                this.style.transform = '';
            }, 100);
        });
    });
}

function enterKioskMode() {
    if (document.documentElement.requestFullscreen) {
        document.documentElement.requestFullscreen();
    } else if (document.documentElement.webkitRequestFullscreen) {
        document.documentElement.webkitRequestFullscreen();
    } else if (document.documentElement.msRequestFullscreen) {
        document.documentElement.msRequestFullscreen();
    }
}

function exitKioskMode() {
    if (document.exitFullscreen) {
        document.exitFullscreen();
    } else if (document.webkitExitFullscreen) {
        document.webkitExitFullscreen();
    } else if (document.msExitFullscreen) {
        document.msExitFullscreen();
    }
}

function handleOrientationChange() {
    if (screen.orientation && screen.orientation.lock) {
        screen.orientation.lock('portrait').catch(err => {
            console.log('Orientation lock not supported:', err);
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    kioskApp = new KioskApp();
    addTouchFeedback();
    handleOrientationChange();
    
    window.addEventListener('orientationchange', handleOrientationChange);
    
});

window.kioskUtils = {
    enterKioskMode,
    exitKioskMode,
    resetToWelcome: () => kioskApp.returnToWelcome(),
    getCurrentScreen: () => kioskApp.currentScreen,
    setInactivityTimeout: (seconds) => {
        kioskApp.inactivityTimeout = seconds * 1000;
        kioskApp.resetInactivityTimer();
    }
};
