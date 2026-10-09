-- Log unique (PC, ROM bank) pairs that read ROM between frames F0..F1, plus every DMA in that window.
-- Finds text/font readers: run with a route that reaches a dialogue box. Globals F0/F1 override the window.
local f0, f1 = F0 or 0, F1 or 1e9
local mem = emu.memType.snesMemory
local seen = {}
local function on() return L.frame >= f0 and L.frame <= f1 end
local function hook(addr, value)
  if not on() then return end
  local s = emu.getState()
  local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
  local key = pc * 256 + (addr >> 16)
  if not seen[key] then
    seen[key] = true
    L.log(string.format("f%d pc=%06X read %06X(off %06X)=%02X A=%04X X=%04X Y=%04X DB=%02X", L.frame, pc, addr,
      L.rom_off(addr), value, s["cpu.a"], s["cpu.x"], s["cpu.y"], s["cpu.dbr"]))
  end
end
for bank = 0, 0xFF do
  if bank < 0x7E or bank > 0x7F then
    emu.addMemoryCallback(L.safe(hook), emu.callbackType.read, (bank << 16) | 0x8000, (bank << 16) | 0xFFFF,
      emu.cpuType.snes, mem)
  end
end
for _, bank in ipairs({ 0x000000, 0x800000 }) do
  emu.addMemoryCallback(L.safe(function(addr, value)
    if not on() then return end
    for ch = 0, 7 do
      if value & (1 << ch) ~= 0 then
        local b = 0x4300 + ch * 16
        local src = emu.read(b + 4, mem) << 16 | emu.read(b + 3, mem) << 8 | emu.read(b + 2, mem)
        L.log(string.format("f%d DMA ch%d src=%06X n=%04X bbus=21%02X vram=%04X", L.frame, ch, src,
          emu.read(b + 6, mem) << 8 | emu.read(b + 5, mem), emu.read(b + 1, mem),
          emu.read(0x2116, emu.memType.snesMemory)))
      end
    end
  end), emu.callbackType.write, bank + 0x420B, bank + 0x420B, emu.cpuType.snes, mem)
end
