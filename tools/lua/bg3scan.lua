-- Every 30 frames, while no message runs ($043E = 0), look for kana tiles (60-9D, A0-D6) on the BG3 tilemap
-- (VRAM word $5800-$5FFF) and save a shot of each new screen: finds Japanese drawn outside the message engine.
local m, vr = emu.memType.snesMemory, emu.memType.snesVideoRam
local seen = {}
L.on_frame(function(f)
  if f % 30 ~= 0 or (emu.read(0x043E, m) | emu.read(0x043F, m)) ~= 0 then return end
  local codes, n = {}, 0
  for a = 0xB000, 0xBFFE, 2 do
    local t = emu.read(a, vr)
    if (t >= 0x60 and t <= 0x9D) or (t >= 0xA0 and t <= 0xD6) then
      n = n + 1
      if n <= 12 then codes[#codes + 1] = string.format("%04X:%02X", a // 2, t) end
    end
  end
  if n >= 3 then
    local key = table.concat(codes, " ")
    if not seen[key] then
      seen[key] = true
      L.log(string.format("f%d kana=%d %s", f, n, key))
      L.shot(string.format("bg3_%06d.png", f))
    end
  end
end)
