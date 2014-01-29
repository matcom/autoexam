class CreatePregunta < ActiveRecord::Migration
  def change
    create_table :pregunta do |t|
      t.text :titulo
      t.integer :asignatura_id
      t.string :etiquetas

      t.timestamps
    end
  end
end
