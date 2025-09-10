  function setup()
      key_enable(5, false)   -- Désactive touche 5
      log("Touche 5 désactivée")
  end

  function on_scan(barcode)
      -- Supprimer CR/LF/espaces du barcode
      local clean_barcode = barcode:gsub("[\r\n%s]+", "")

      log("Barcode brut: '" .. barcode .. "'")
      log("Barcode nettoyé: '" .. clean_barcode .. "'")
      log("Longueur brut: " .. #barcode .. " / nettoyé: " .. #clean_barcode)
      if clean_barcode == "ENABLE_ALL" then
          for i=0,19 do
              key_enable(i, true)
          end
          log('✅ Barcode == ENABLE_ALL')
          melody("SUCCESS")
      elseif clean_barcode == "DISABLE_ALL" then
          for i=0,19 do
              key_enable(i, false)
          end
          log('✅ Barcode == DISABLE_ALL')
          melody("SUCCESS")
      else
          log("Barcode normal: " .. clean_barcode)
          key(clean_barcode .. "\n")
      end
  end
