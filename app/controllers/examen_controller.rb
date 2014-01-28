class ExamenController < ApplicationController
  before_action :set_examan, only: [:show, :edit, :update, :destroy]

  # GET /examen
  # GET /examen.json
  def index
    @examen = Examan.all
  end

  # GET /examen/1
  # GET /examen/1.json
  def show
  end

  # GET /examen/new
  def new
    @examan = Examan.new
  end

  # GET /examen/1/edit
  def edit
  end

  # POST /examen
  # POST /examen.json
  def create
    @examan = Examan.new(examan_params)

    respond_to do |format|
      if @examan.save
        format.html { redirect_to @examan, notice: 'Examan was successfully created.' }
        format.json { render action: 'show', status: :created, location: @examan }
      else
        format.html { render action: 'new' }
        format.json { render json: @examan.errors, status: :unprocessable_entity }
      end
    end
  end

  # PATCH/PUT /examen/1
  # PATCH/PUT /examen/1.json
  def update
    respond_to do |format|
      if @examan.update(examan_params)
        format.html { redirect_to @examan, notice: 'Examan was successfully updated.' }
        format.json { head :no_content }
      else
        format.html { render action: 'edit' }
        format.json { render json: @examan.errors, status: :unprocessable_entity }
      end
    end
  end

  # DELETE /examen/1
  # DELETE /examen/1.json
  def destroy
    @examan.destroy
    respond_to do |format|
      format.html { redirect_to examen_url }
      format.json { head :no_content }
    end
  end

  private
    # Use callbacks to share common setup or constraints between actions.
    def set_examan
      @examan = Examan.find(params[:id])
    end

    # Never trust parameters from the scary internet, only allow the white list through.
    def examan_params
      params.require(:examan).permit(:nombre, :etiquetas, :directorio, :cantidad)
    end
end
