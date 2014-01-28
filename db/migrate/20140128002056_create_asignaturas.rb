class CreateAsignaturas < ActiveRecord::Migration
  def change
    create_table :asignaturas do |t|
      t.string :nombre_corto
      t.string :nombre_largo
      t.text :descripcion

      t.timestamps
    end
  end
end
