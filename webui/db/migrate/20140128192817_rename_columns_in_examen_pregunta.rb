class RenameColumnsInExamenPregunta < ActiveRecord::Migration
  def change
    rename_column :examen_pregunta, :examen_id, :examan_id
    rename_column :examen_pregunta, :prueba_id, :preguntum_id
  end
end
