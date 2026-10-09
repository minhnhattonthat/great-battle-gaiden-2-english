-- Log each distinct string pointer the dialogue reader ($88:A168) starts on ($1E0A = 0): "ptr XXXXXX fN".
-- Compare against the extracted pointer set (tools/textcover.py) to find text sources not yet extracted.
local m = emu.memType.snesMemory
local seen = {}
L.on_exec(0x88A168, 0x88A168, function()
  if (emu.read(0x1E0A, m) | emu.read(0x1E0B, m) << 8) ~= 0 then return end
  local p = emu.read(0x1CFB, m) | emu.read(0x1CFC, m) << 8 | emu.read(0x1CFD, m) << 16
  if not seen[p] then
    seen[p] = true
    L.log(string.format("ptr %06X f%d", p, L.frame))
  end
end)
