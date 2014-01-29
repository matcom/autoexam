class RenameExamensPreguntasToExamenPregunta < ActiveRecord::Migration
  def change
    rename_table :examens_preguntas, :examen_pregunta
  end
end
