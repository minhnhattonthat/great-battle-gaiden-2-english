-- Dump VRAM (64 KB), CGRAM (512 B), OAM (544 B) and PPU state at frame DUMP_AT (default: FRAMES - 3) into OUT:
-- vram.bin, cgram.bin, oam.bin, ppu.txt. Read with tools/gfx.py.
local function grab(mt, n)
  local t = {}
  for a = 0, n - 1 do t[#t + 1] = string.char(emu.read(a, mt)) end
  return table.concat(t)
end
local function dump()
  L.write_file(OUT .. "vram.bin", grab(emu.memType.snesVideoRam, 0x10000))
  L.write_file(OUT .. "cgram.bin", grab(emu.memType.snesCgRam, 0x200))
  L.write_file(OUT .. "oam.bin", grab(emu.memType.snesSpriteRam, 0x220))
  local s, keys = emu.getState(), {}
  for k, v in pairs(s) do if k:find("^ppu") then keys[#keys + 1] = k .. "=" .. tostring(v) end end
  table.sort(keys)
  L.write_file(OUT .. "ppu.txt", table.concat(keys, "\n"))
end
L.on_frame(function(f) if f == (DUMP_AT or FRAMES - 3) then dump() end end)
