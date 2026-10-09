-- At frame DUMP_AT (default end of run) log the 128 OAM buffer entries at $7E:0200 (x, y, tile, attr) and the PCs
-- that wrote into $0200-$041F during the last 5 frames before it.
local at = DUMP_AT or (FRAMES - 3)
local m = emu.memType.snesMemory
local writers = {}
for _, base in ipairs({ 0x000200, 0x800200, 0x7E0200 }) do
  L.on_write(base, base + 0x21F, function(addr)
    if L.frame >= at - 5 and L.frame < at then
      local s = emu.getState()
      local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
      writers[pc] = (writers[pc] or 0) + 1
    end
  end)
end
L.on_frame(function(f)
  if f ~= at then return end
  for i = 0, 127 do
    local b = 0x7E0200 + i * 4
    local x, y, t, a = emu.read(b, m), emu.read(b + 1, m), emu.read(b + 2, m), emu.read(b + 3, m)
    if y ~= 0xF0 and y ~= 0xE0 then L.log(string.format("obj%3d x=%3d y=%3d tile=%02X attr=%02X", i, x, y, t, a)) end
  end
  for pc, n in pairs(writers) do L.log(string.format("writer %06X x%d", pc, n)) end
end)
