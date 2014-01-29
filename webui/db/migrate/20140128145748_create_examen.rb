class CreateExamen < ActiveRecord::Migration
  def change
    create_table :examen do |t|
      t.string :nombre
      t.string :etiquetas
      t.string :directorio
      t.integer :cantidad

      t.timestamps
    end
  end
end
