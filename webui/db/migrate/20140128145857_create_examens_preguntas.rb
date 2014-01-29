class CreateExamensPreguntas < ActiveRecord::Migration
  def change
    create_table :examens_preguntas, :index => false do |t|
      t.integer :examen_id
      t.integer :prueba_id
    end
  end
end
