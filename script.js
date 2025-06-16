class KioskApp {
    constructor() {
        this.currentScreen = 'welcome-screen';
        this.navigationHistory = [];
        this.inactivityTimer = null;
        this.inactivityTimeout = 30000; // 30 seconds
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.startInactivityTimer();
        this.showScreen('welcome-screen');
        this.updateBreadcrumb();
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
            this.updateBreadcrumb();
        }

        this.resetInactivityTimer();
    }

    updateBreadcrumb() {
        const breadcrumbText = document.getElementById('breadcrumb-text');
        if (!breadcrumbText) return;

        const breadcrumbMap = {
            'welcome-screen': 'Home',
            'main-menu': 'Home > Main Menu',
            'about-ecosystem': 'Home > About Ecosystem',
            'ecosystem-overview': 'Home > About Ecosystem > Overview',
            'key-statistics': 'Home > About Ecosystem > Statistics',
            'skills-gap-challenge': 'Home > About Ecosystem > Overview > Skills Gap',
            'three-pillar-solution': 'Home > About Ecosystem > Overview > Solution',
            'why-matters-now': 'Home > About Ecosystem > Overview > Why Now',
            'three-organizations': 'Home > Three Organizations',
            'icr247-details': 'Home > Three Organizations > ICR247',
            'gennflex-details': 'Home > Three Organizations > GennFlex',
            'gakuto-details': 'Home > Three Organizations > Gakuto Club',
            'icr247-overview': 'Home > Three Organizations > ICR247 > Overview',
            'icr247-services': 'Home > Three Organizations > ICR247 > Services',
            'icr247-education': 'Home > Three Organizations > ICR247 > Education',
            'revolutionary-methods': 'Home > Revolutionary Methods',
            'hands-on-learning': 'Home > Revolutionary Methods > Hands-On Learning',
            'technology-integration': 'Home > Revolutionary Methods > Technology',
            'impact-stories': 'Home > Impact & Success',
            'future-vision': 'Home > Future Vision',
            'contact-learn': 'Home > Contact & Learn More',
            'organizations-contact': 'Home > Contact & Learn More > Organizations',
            'get-involved': 'Home > Contact & Learn More > Get Involved'
        };

        breadcrumbText.textContent = breadcrumbMap[this.currentScreen] || 'Home';
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

function showSection(sectionId) {
    kioskApp.showScreen(sectionId);
}

function showSubsection(subsectionId) {
    kioskApp.showScreen(subsectionId);
}

function showDetail(detailId) {
    kioskApp.showScreen(detailId);
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
