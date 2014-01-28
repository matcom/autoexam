class AddPreguntasPorEtiquetaToExamen < ActiveRecord::Migration
  def change
    add_column :examen, :preguntas_por_tema, :string
  end
end
