'use strict';
const CACHE_NAME = 'flutter-app-cache';
const RESOURCES = {
  "favicon.png": "5dcef449791fa27946b3d35ad8803796",
"index.html": "32db3c4219525a6faca41cbf42a08fa8",
"/": "32db3c4219525a6faca41cbf42a08fa8",
"assets/LICENSE": "8d449c64ffba3d3e385da3b61d47e572",
"assets/assets/fonts/Alegreya-BoldItalic.ttf": "a6bf3e4d95c75fb9905498616449f113",
"assets/assets/images/corona_splash_screen_image.png": "d4b0481bdca571cff9dc157f275ec084",
"assets/assets/images/how_to_use_update_map.png": "114a347da51d009bdb223ca388ccf8e4",
"assets/assets/images/how_to_use_app_stats.png": "ada41f0a9e995390c5bcad50ded306ed",
"assets/assets/images/how_to_use_health_toggle.png": "0cbfaf598658ff93085a47f336cc138e",
"assets/assets/images/how_to_use_share_status.png": "434bec446883af74e5cf3342ef3e4e44",
"assets/assets/images/landing_page_background.png": "c68fe86d6367d8ec1195bb2c9f5f65c1",
"assets/assets/images/landing_page/landing_page_Sheet_5.png": "9bc5f58b50c360146a849ed3b903b5d9",
"assets/assets/images/landing_page/landing_page_Sheet_2.png": "fe17a2b11e8bf5ba406e82ac1c7b6bc8",
"assets/assets/images/landing_page/landing_page_Sheet_3.png": "3e5db64e7e9c3a100a2d22389e45c540",
"assets/assets/images/landing_page/landing_page_Sheet_6.png": "eedd00dc8b7ba477f61db35e5bb713ad",
"assets/assets/images/landing_page/landing_page_Sheet_4.png": "9b9deec557b9e36e39ed30cb21722bed",
"assets/assets/images/landing_page/landing_page_Sheet_1.png": "ceeafcea4edf9706d7d87e4701dfe809",
"assets/assets/images/how_to_use_live_map.jpg": "6be9ccaaa50de6dfea1c12ebfa3567de",
"assets/assets/images/try%2520marker.png": "5da33a8e758e035b97b1286f4014c527",
"assets/AssetManifest.json": "3c9154f40f84944a83b1996b6a9b714f",
"assets/fonts/MaterialIcons-Regular.ttf": "56d3ffdef7a25659eab6a68a3fbfaf16",
"assets/FontManifest.json": "916fef6c0afd25990b14c49164d9da18",
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
"main.dart.js": "f512dbdb2179ff211071171f87139946",
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
