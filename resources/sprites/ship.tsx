<?xml version="1.0" encoding="UTF-8"?>
<tileset version="1.4" tiledversion="1.4.3" name="ship" tilewidth="16" tileheight="24" tilecount="10" columns="5">
 <image source="ship.png" width="80" height="48"/>
 <tile id="1">
  <animation>
   <frame tileid="1" duration="100"/>
   <frame tileid="6" duration="100"/>
   <frame tileid="0" duration="100"/>
   <frame tileid="5" duration="100"/>
   <frame tileid="1" duration="100"/>
   <frame tileid="6" duration="100"/>
  </animation>
 </tile>
 <tile id="2">
  <objectgroup draworder="index" id="2">
   <object id="1" x="0" y="0" width="16" height="15"/>
  </objectgroup>
  <animation>
   <frame tileid="2" duration="100"/>
   <frame tileid="7" duration="100"/>
  </animation>
 </tile>
 <tile id="3">
  <animation>
   <frame tileid="3" duration="100"/>
   <frame tileid="8" duration="100"/>
   <frame tileid="4" duration="100"/>
   <frame tileid="9" duration="100"/>
  </animation>
 </tile>
</tileset>
