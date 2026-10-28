// Squelette de rendu MCU pour un cadran WFF tiers.
// À ADAPTER : positions, images, données. Écrit from scratch pour l'API du moteur MCU
// (type LVGL) observée par rétro-ingénierie — aucun code OnePlus copié.
// Interopérabilité / usage personnel. Non testé sur matériel (exige root + SysUI patché).
//
// Objets globaux fournis par le moteur MCU :
//   Watchface()  -> wfInfo.{year,month,day,week,hour,min,sec,battery,steps,calorie,
//                           styleIndex,language,rsMode,updataFlag}
//   WatchfaceUpdata.{hour,min,sec,day,mon,week,step,calories,battery}  (masque de changement)
//   View / Image / Label / EditWidget / FileManager / JumpApp
//   WindowEvent.{winTop,winResume,winReenter,minTimeout,secTimeout,winRepaint,timeChange,userData}
//   WatchfaceJump.{bigCoreApp,bigCoreFace}
require('js_asset.js');

var mywatchface = {
    name: 'mywatchface',

    onCreate: function(par, hor_res, ver_res) {
        var page = View(par, 0, 0, hor_res, ver_res);
        page.setLocalStyle({ 'main:default': { 'bg-color': 0x000000, 'border-side': 0x00, 'radius': 0, 'pad-all': 0 } });
        this.par = page;
        this.init(page);
        return page;
    },

    init: function(par) {
        this.wfInfo = Watchface();

        // Fond plein écran (optionnel). Commente si pas d'image de fond.
        Image(par, PicId.Picbg, 0, 0);

        // Heure HH:MM en grands chiffres (positions à ajuster à ton design 466x466).
        this.hH = Image(par, PicId.Pic0,  83, 160);
        this.hL = Image(par, PicId.Pic0, 149, 160);
        Image(par, PicId.Picmaohao,      215, 160);
        this.mH = Image(par, PicId.Pic0, 251, 160);
        this.mL = Image(par, PicId.Pic0, 317, 160);

        // Date (libellé). setFont(FontId.Fontdata) suppose la police embarquée.
        this.date = Label(par, StringId.Stringmonth_1, 100, 110, 267, 40);
        this.date.textAlign = TextAlign.center;
        this.date.setColor(0x9A, 0xE6, 0xFF);     // cyan « data-stream »

        // Ligne de données : batterie + pas (exemple).
        this.data = Label(par, StringId.Stringname, 100, 300, 267, 36);
        this.data.textAlign = TextAlign.center;
        this.data.setColor(0xFE, 0x7C, 0x48);     // orange accent

        this.draw();
        return 0;
    },

    draw: function() {
        var num = [PicId.Pic0,PicId.Pic1,PicId.Pic2,PicId.Pic3,PicId.Pic4,
                   PicId.Pic5,PicId.Pic6,PicId.Pic7,PicId.Pic8,PicId.Pic9];
        var f = this.wfInfo.updataFlag;

        if ((WatchfaceUpdata.hour & f) || (WatchfaceUpdata.min & f)) {
            this.hH.setPic(num[(this.wfInfo.hour / 10) << 0]);
            this.hL.setPic(num[this.wfInfo.hour % 10]);
            this.mH.setPic(num[(this.wfInfo.min / 10) << 0]);
            this.mL.setPic(num[this.wfInfo.min % 10]);
        }
        if ((WatchfaceUpdata.mon & f) || (WatchfaceUpdata.day & f) || (WatchfaceUpdata.week & f)) {
            var wk = [StringId.Stringsun,StringId.Stringmon,StringId.Stringtue,StringId.Stringwed,
                      StringId.Stringthu,StringId.Stringfri,StringId.Stringsat];
            this.date.setFont(FontId.Fontdata);
            this.date.print("%s %02d", wk[this.wfInfo.week], this.wfInfo.day);
        }
        if ((WatchfaceUpdata.battery & f) || (WatchfaceUpdata.step & f)) {
            this.data.setFont(FontId.Fontdata);
            this.data.print("%d%%  %d", this.wfInfo.battery, this.wfInfo.steps);
        }
    },

    onEvent: function(event) {
        switch (event) {
            case WindowEvent.winTop:
            case WindowEvent.winResume:
            case WindowEvent.winReenter:
            case WindowEvent.minTimeout:
            case WindowEvent.winRepaint:
            case WindowEvent.timeChange:
                // Sortie de veille / mode plein : rendre la main au gros cœur (rendu riche).
                if (this.wfInfo.rsMode == false) {
                    JumpApp(WatchfaceJump.bigCoreFace, 1);
                    return 0;
                }
                this.draw();
                break;
        }
        return 0;
    },

    onDestory: function(event) { return 0; }
};

!subwm.registerSubWindow(mywatchface);
mywatchface = null;
