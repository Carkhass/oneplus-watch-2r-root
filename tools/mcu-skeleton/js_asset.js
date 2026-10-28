// Énumérations partagées du rendu MCU — à garder cohérentes avec l'ordre des images
// passées à mkpicbin.py (PicId) et avec les fonts/strings embarquées.
// Squelette pour cadran WFF tiers « data-stream ». Interopérabilité / usage personnel.

var PicId = {
    Pic0: 0, Pic1: 1, Pic2: 2, Pic3: 3, Pic4: 4,
    Pic5: 5, Pic6: 6, Pic7: 7, Pic8: 8, Pic9: 9,
    Picmaohao: 10,   // deux-points ":"
    Picbg: 11,       // fond plein écran (466x466), idéalement BGRA8888 ou ARGB4444
};

var FontId = {
    Fontname: 0,
    Fontdata: 1,     // police pour la date / libellés
};

var StringId = {
    Stringname: 0,
    Stringday: 1,
    Stringmonth_1: 2, Stringmonth_2: 3, Stringmonth_3: 4, Stringmonth_4: 5,
    Stringmonth_5: 6, Stringmonth_6: 7, Stringmonth_7: 8, Stringmonth_8: 9,
    Stringmonth_9: 10, Stringmonth_10: 11, Stringmonth_11: 12, Stringmonth_12: 13,
    Stringsun: 14, Stringmon: 15, Stringtue: 16, Stringwed: 17,
    Stringthu: 18, Stringfri: 19, Stringsat: 20,
};
