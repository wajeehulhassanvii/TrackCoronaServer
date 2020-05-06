'use strict';
const CACHE_NAME = 'flutter-app-cache';
const RESOURCES = {
  "favicon.png": "5dcef449791fa27946b3d35ad8803796",
"index.html": "32db3c4219525a6faca41cbf42a08fa8",
"/": "32db3c4219525a6faca41cbf42a08fa8",
"assets/LICENSE": "7ba970b84a44b53380170f8b02e47c53",
"assets/assets/fonts/Alegreya-BoldItalic.ttf": "a6bf3e4d95c75fb9905498616449f113",
"assets/assets/images/corona_splash_screen_image.png": "d4b0481bdca571cff9dc157f275ec084",
"assets/assets/images/how_to_use_update_map.png": "114a347da51d009bdb223ca388ccf8e4",
"assets/assets/images/how_to_use_app_stats.png": "ada41f0a9e995390c5bcad50ded306ed",
"assets/assets/images/how_to_use_health_toggle.png": "0cbfaf598658ff93085a47f336cc138e",
"assets/assets/images/how_to_use_share_status.png": "434bec446883af74e5cf3342ef3e4e44",
"assets/assets/images/dodgecorona_logo_simple.png": "fbdd5b8f2f0220b7f6dcf56e2c4310a7",
"assets/assets/images/in_app_transparent_logo.png": "e87255e7c036c542a33a899585f1b736",
"assets/assets/images/landing_page_background.png": "c68fe86d6367d8ec1195bb2c9f5f65c1",
"assets/assets/images/landing_page/dodgecorona_logo_simple.png": "b2179579306e6a5b7998d639f36d9a26",
"assets/assets/images/landing_page/landing_page_Sheet_5.png": "9bc5f58b50c360146a849ed3b903b5d9",
"assets/assets/images/landing_page/landing_page_Sheet_2.png": "fe17a2b11e8bf5ba406e82ac1c7b6bc8",
"assets/assets/images/landing_page/landing_page_Sheet_3.png": "3e5db64e7e9c3a100a2d22389e45c540",
"assets/assets/images/landing_page/landing_page_Sheet_6.png": "eedd00dc8b7ba477f61db35e5bb713ad",
"assets/assets/images/landing_page/landing_page_Sheet_4.png": "9b9deec557b9e36e39ed30cb21722bed",
"assets/assets/images/landing_page/landing_page_Sheet_1.png": "ceeafcea4edf9706d7d87e4701dfe809",
"assets/assets/images/how_to_use_live_map.jpg": "6be9ccaaa50de6dfea1c12ebfa3567de",
"assets/assets/images/try%2520marker.png": "5da33a8e758e035b97b1286f4014c527",
"assets/assets/images/dodgecorona_logo_simple_curved.png": "124a26b56e93a78f215839d35589aaac",
"assets/assets/images/how_to_use/ho_to_use_zoom_buttons.png": "274e4216c434033bfdfe84171ee86a59",
"assets/assets/images/how_to_use/ho_to_use_stats.png": "dad49f8ca93c544d6a6b9f24cffd76f7",
"assets/assets/images/how_to_use/ho_to_use_live_map_connection.png": "d36e60368a174a65971ef05245bdc2be",
"assets/assets/images/how_to_use/ho_to_use_status_on_screen.png": "febb9017c6a05d04954ffa54bc583e0c",
"assets/assets/images/how_to_use/ho_to_use_clear_button.png": "45bc23eada6aacd101d3b66d6575a23b",
"assets/assets/images/how_to_use/ho_to_use_toggle_well_symptoms_infected.png": "58c6ba0ac93c82dac559de1662266fb0",
"assets/assets/images/how_to_use/ho_to_use_share_status.png": "bfbba24853f86bf3c8ad793dbc517405",
"assets/assets/images/how_to_use/ho_to_use_update_map_button.png": "05d18b534faea6d25273b12378383a62",
"assets/AssetManifest.json": "189060065483b332517acddb7209eec4",
"assets/fonts/MaterialIcons-Regular.ttf": "56d3ffdef7a25659eab6a68a3fbfaf16",
"assets/FontManifest.json": "55b0589869c59d4771eee2fff5074d7d",
"assets/packages/cupertino_icons/assets/CupertinoIcons.ttf": "115e937bb829a890521f72d2e664b632",
"assets/packages/awesome_dialog/assets/flare/succes_without_loop.flr": "3d8b3b3552370677bf3fb55d0d56a152",
"assets/packages/awesome_dialog/assets/flare/succes.flr": "ebae20460b624d738bb48269fb492edf",
"assets/packages/awesome_dialog/assets/flare/warning_without_loop.flr": "c84f528c7e7afe91a929898988012291",
"assets/packages/awesome_dialog/assets/flare/error_without_loop.flr": "35b9b6c9a71063406bdac60d7b3d53e8",
"assets/packages/awesome_dialog/assets/flare/error.flr": "87d83833748ad4425a01986f2821a75b",
"assets/packages/awesome_dialog/assets/flare/info.flr": "bc654ba9a96055d7309f0922746fe7a7",
"assets/packages/awesome_dialog/assets/flare/info_without_loop.flr": "cf106e19d7dee9846bbc1ac29296a43f",
"assets/packages/awesome_dialog/assets/flare/warning.flr": "68898234dacef62093ae95ff4772509b",
"assets/packages/line_awesome_icons/assets/fonts/icon_font.ttf": "4d42f5f0c62a8f51e876c14575354a6e",
"manifest.json": "34c23f28bf40df5e928b35f846283dd6",
"main.dart.js": "36bd146e5ccfa7e93d370b5c75e1c30f",
"icons/Icon-512.png": "96e752610906ba2a93c65f8abe1645f1",
"icons/Icon-192.png": "ac9a721a12bbc803b44f645561ecb1e1"
};

self.addEventListener('activate', function (event) {
  event.waitUntil(
    caches.keys().then(function (cacheName) {
      return caches.delete(cacheName);
    }).then(function (_) {
      return caches.open(CACHE_NAME);
    }).then(function (cache) {
      return cache.addAll(Object.keys(RESOURCES));
    })
  );
});

self.addEventListener('fetch', function (event) {
  event.respondWith(
    caches.match(event.request)
      .then(function (response) {
        if (response) {
          return response;
        }
        return fetch(event.request);
      })
  );
});
